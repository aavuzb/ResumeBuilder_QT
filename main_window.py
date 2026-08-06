"""
main_window.py
The main application window: a sidebar wizard on the left, the active
form section in the middle, and a live resume preview on the right.
"""

import json

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPlainTextEdit, QPushButton, QSplitter, QStackedWidget, QVBoxLayout, QWidget,
)

import theme
from docx_engine import (
    DEFAULT_CONTACT_ORDER, DEFAULT_SECTION_ORDER, build_resume, build_resume_pdf,
    resolve_contact_order, resolve_section_order,
)
from i18n import DEFAULT_LANGUAGE, LANGUAGES, set_language, t
from preview import PreviewPanel
from resume_style import DEFAULT_STYLE, resolve_style
from sample_data import SAMPLE
from style_dialog import StyleDialog
from widgets import (
    EducationList, ExperienceList, LabelValueList, NavButton, PublicationList,
    ReorderableRow, add_field, button, hairline, make_line_edit, make_scroll_page,
    micro_label, section_header, update_row_arrow_states,
)


class PdfExportThread(QThread):
    """Runs the (blocking) docx -> PDF conversion off the UI thread."""

    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, data, path, parent=None):
        super().__init__(parent)
        self.data = data
        self.path = path

    def run(self):
        try:
            build_resume_pdf(self.data, self.path)
        except Exception as exc:  # noqa: BLE001 — surfaced to the user as-is
            self.failed.emit(str(exc))
            return
        self.succeeded.emit(self.path)


class MainWindow(QMainWindow):
    # Fixed, language-independent order of keys; display labels are looked
    # up fresh (via _section_labels()) each time the sidebar is built, so
    # they always reflect the currently active language.
    SECTION_KEYS = [
        "personal", "summary", "skills", "experience", "education",
        "publications", "certificates", "additional", "generate",
    ]

    def _section_labels(self):
        return {
            "personal": t("nav.personal"), "summary": t("nav.summary"),
            "skills": t("nav.skills"), "experience": t("nav.experience"),
            "education": t("nav.education"), "publications": t("nav.publications"),
            "certificates": t("nav.certificates"), "additional": t("nav.additional"),
            "generate": t("nav.generate"),
        }

    def __init__(self):
        super().__init__()
        self.resize(1580, 940)
        self.setMinimumSize(1180, 720)

        self.nav_buttons = {}
        self.pages = {}
        self.page_index = {}
        self.eyebrow_labels = {}
        self._pdf_thread = None
        self._active_field = None
        self._active_field_precise = None
        # The app's own interface language — separate from whatever
        # language the user's resume content happens to be written in.
        self.language = DEFAULT_LANGUAGE
        set_language(self.language)
        # The 7 sections between the fixed Personal Info / Preview & Generate
        # bookends — everyone drafts a resume in a different order, so these
        # are freely reorderable via the sidebar's up/down controls.
        self.section_order = list(DEFAULT_SECTION_ORDER)
        # Location/Phone/Email/Visa share one contact line — also freely
        # reorderable, independently of the section order above.
        self.contact_order = list(DEFAULT_CONTACT_ORDER)
        # Font/sizes/colors/page background for the resume itself — separate
        # from theme.py, which only styles this app's own navy/brass chrome.
        self.style = dict(DEFAULT_STYLE)
        self._style_dialog = None

        self._build_layout()
        self._apply_data(SAMPLE)
        self._select_section("personal")

        QApplication.instance().focusChanged.connect(self._on_focus_changed)

        self._sync_timer = QTimer(self)
        self._sync_timer.setInterval(700)
        self._sync_timer.timeout.connect(self._on_sync_tick)
        self._sync_timer.start()

        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self._set_status(t("status.ready"), ""))

    # ---------------------------------------------------------------- layout --
    def _build_layout(self):
        self.setWindowTitle(t("app.window_title"))
        central = QWidget()
        central.setObjectName("RootBg")
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(1)

        self.stack = QStackedWidget()
        self.stack.setObjectName("FormArea")
        self._build_pages()
        self.splitter.addWidget(self.stack)

        self.preview_panel = PreviewPanel()
        self.preview_panel.style_requested.connect(self._open_style_dialog)
        self.splitter.addWidget(self.preview_panel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([820, 720])

        root.addWidget(self.splitter, 1)
        self.setCentralWidget(central)

        self.status = self.statusBar()
        self.status_label = QLabel(t("status.ready"))
        self.status_label.setStyleSheet(f"color: {theme.TEXT_GRAY};")
        self.status_label.setContentsMargins(4, 0, 4, 0)
        self.status.addWidget(self.status_label)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(262)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 26, 0, 16)
        layout.setSpacing(0)

        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(22, 0, 22, 0)
        badge = QLabel("R")
        badge.setObjectName("BrandBadge")
        badge.setFixedSize(38, 38)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFont(theme.serif_font(17, weight=700))

        brand_text = QVBoxLayout()
        brand_text.setSpacing(1)
        brand_title = QLabel(t("app.brand_title"))
        brand_title.setObjectName("BrandTitle")
        brand_title.setFont(theme.serif_font(14, weight=700))
        brand_title.setWordWrap(True)
        brand_tag = QLabel(t("app.brand_tag"))
        brand_tag.setObjectName("BrandTag")
        brand_tag.setFont(theme.base_font(9))
        brand_tag.setWordWrap(True)
        brand_text.addWidget(brand_title)
        brand_text.addWidget(brand_tag)

        brand_row.addWidget(badge)
        brand_row.addSpacing(10)
        brand_row.addLayout(brand_text)
        brand_row.addStretch(1)
        layout.addLayout(brand_row)

        layout.addSpacing(16)
        lang_row = QHBoxLayout()
        lang_row.setContentsMargins(22, 0, 22, 0)
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("SidebarLanguageCombo")
        self.language_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        lang_codes = list(LANGUAGES.keys())
        for code in lang_codes:
            self.language_combo.addItem(f"🌐  {LANGUAGES[code]}", code)
        self.language_combo.setCurrentIndex(lang_codes.index(self.language))
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_row.addWidget(self.language_combo, 1)
        layout.addLayout(lang_row)

        layout.addSpacing(16)
        top_hairline = QFrame()
        top_hairline.setObjectName("SidebarHairline")
        layout.addWidget(top_hairline)
        layout.addSpacing(10)

        section_labels = self._section_labels()
        total_steps = len(self.SECTION_KEYS)

        personal_btn = NavButton("01", section_labels["personal"], key="personal")
        personal_btn.clicked.connect(lambda checked: self._select_section("personal"))
        layout.addWidget(personal_btn)
        self.nav_buttons["personal"] = personal_btn

        # Reorderable middle section — self._movable_insert_index marks the
        # layout slot where these buttons live, so _rebuild_sidebar_order()
        # can pull them out and reinsert them in a new sequence later.
        self.sidebar_layout = layout
        self._movable_insert_index = layout.count()

        for i, key in enumerate(self.section_order):
            btn = NavButton(f"{i + 2:02d}", section_labels[key], key=key, movable=True)
            btn.clicked.connect(lambda checked, k=key: self._select_section(k))
            btn.move_requested.connect(lambda delta, k=key: self._move_section(k, delta))
            btn.drop_requested.connect(self._on_section_dropped)
            layout.addWidget(btn)
            self.nav_buttons[key] = btn

        self.reset_order_btn = QPushButton(t("common.reset_order"))
        self.reset_order_btn.setObjectName("SidebarResetOrderButton")
        self.reset_order_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_order_btn.clicked.connect(self._reset_section_order)
        reset_row = QHBoxLayout()
        reset_row.setContentsMargins(22, 2, 15, 6)
        reset_row.addWidget(self.reset_order_btn)
        reset_row.addStretch(1)
        layout.addLayout(reset_row)

        generate_btn = NavButton(f"{total_steps:02d}", section_labels["generate"], key="generate")
        generate_btn.clicked.connect(lambda checked: self._select_section("generate"))
        generate_btn.dot_label.hide()
        layout.addWidget(generate_btn)
        self.nav_buttons["generate"] = generate_btn

        self._update_arrow_states()
        self._update_reset_visibility()

        layout.addStretch(1)

        bottom_hairline = QFrame()
        bottom_hairline.setObjectName("SidebarHairline")
        layout.addWidget(bottom_hairline)
        layout.addSpacing(12)

        self.toggle_preview_btn = QPushButton(t("common.hide_preview"))
        self.toggle_preview_btn.setObjectName("SidebarGhostButton")
        self.toggle_preview_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_preview_btn.clicked.connect(self._toggle_preview)
        self._preview_toggle_buttons = [self.toggle_preview_btn]
        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(22, 0, 22, 10)
        footer_row.addWidget(self.toggle_preview_btn)
        layout.addLayout(footer_row)

        note = QLabel(t("app.footer_note"))
        note.setObjectName("SidebarFooterNote")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(note)

        return sidebar

    def _toggle_preview(self):
        showing = self.preview_panel.isVisible()
        self.preview_panel.setVisible(not showing)
        text = t("common.show_preview") if showing else t("common.hide_preview")
        # More than one button controls this (the sidebar footer and the
        # one on Preview & Generate) — keep every one of them in sync,
        # regardless of which was clicked.
        for btn in self._preview_toggle_buttons:
            btn.setText(text)

    # ------------------------------------------------------------ language --
    def _on_language_changed(self, index):
        code = self.language_combo.itemData(index)
        if not code or code == self.language:
            return
        data = self._collect_data()
        data["language"] = code
        self._apply_data(data)

    # --------------------------------------------------------- resume style --
    def _open_style_dialog(self):
        if self._style_dialog is None:
            self._style_dialog = StyleDialog(self.style, self)
            self._style_dialog.style_changed.connect(self._on_style_changed)
        else:
            self._style_dialog.set_style(self.style)
        self._style_dialog.show()
        self._style_dialog.raise_()
        self._style_dialog.activateWindow()

    def _on_style_changed(self, new_style):
        self.style = new_style
        self.preview_panel.update_data(
            self._collect_data(), active_field=self._active_field,
            active_field_precise=self._active_field_precise, force=True,
        )
        self._set_status(t("status.resume_style_updated"), "ok")

    # ----------------------------------------------------------------- pages --
    def _add_page(self, key, scroll_widget):
        idx = self.stack.addWidget(scroll_widget)
        self.pages[key] = scroll_widget
        self.page_index[key] = idx

    def _build_pages(self):
        self._build_personal_page()
        self._build_summary_page()
        self._build_skills_page()
        self._build_experience_page()
        self._build_education_page()
        self._build_publications_page()
        self._build_certificates_page()
        self._build_additional_page()
        self._build_generate_page()

    def _build_personal_page(self):
        scroll, layout = make_scroll_page()
        section_header(layout, f'{t("app.step")} 1', t("personal.step_title"), t("personal.step_hint"))

        # Name and title are always first; everything below is freely
        # reorderable (see the contact-field block further down).
        self.personal_fields = {}
        fixed_fields = [
            ("name", t("personal.full_name"), "personal.name"),
            ("title", t("personal.professional_title"), "personal.title"),
        ]
        for i, (key, label, path) in enumerate(fixed_fields):
            edit = make_line_edit()
            edit.setMinimumHeight(36)
            edit._field_path_fn = lambda p=path: p
            edit._field_precise_fn = lambda p=path: p
            add_field(layout, label, edit, gap_before=0 if i == 0 else 14)
            self.personal_fields[key] = edit

        layout.addSpacing(22)
        layout.addWidget(micro_label(t("personal.contact_details")))
        layout.addSpacing(4)
        contact_hint = QLabel(t("personal.contact_hint"))
        contact_hint.setProperty("role", "hint")
        contact_hint.setWordWrap(True)
        layout.addWidget(contact_hint)
        layout.addSpacing(10)

        self.contact_rows_container = QVBoxLayout()
        self.contact_rows_container.setSpacing(8)
        layout.addLayout(self.contact_rows_container)

        self.contact_field_rows = {}
        contact_labels = {
            "location": t("personal.location"), "phone": t("personal.phone"),
            "email": t("personal.email"), "visa": t("personal.visa"),
        }
        for key in self.contact_order:
            self._build_contact_field_row(key, contact_labels[key])
        self._update_contact_arrows()

        layout.addSpacing(22)
        layout.addWidget(hairline())
        layout.addSpacing(18)
        layout.addWidget(micro_label(t("personal.links_title")))
        layout.addSpacing(4)
        hint = QLabel(t("personal.links_hint"))
        hint.setProperty("role", "hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addSpacing(10)
        self.links_list = LabelValueList(
            t("personal.add_link"), field_prefix="links",
            label_placeholder=t("personal.link_label_placeholder"), value_placeholder=t("common.url_placeholder"),
        )
        layout.addWidget(self.links_list)

        layout.addStretch(1)
        self._add_page("personal", scroll)

    def _build_contact_field_row(self, key, label_text):
        row = ReorderableRow()
        row.setObjectName("Row")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 9, 10, 9)
        row_layout.setSpacing(10)

        row_layout.addWidget(row.make_handle())

        content = QVBoxLayout()
        content.setSpacing(4)
        content.addWidget(micro_label(label_text))
        edit = make_line_edit()
        edit.setMinimumHeight(34)
        edit._field_path_fn = lambda: "personal.contact"
        edit._field_precise_fn = lambda k=key: f"personal.contact.{k}"
        content.addWidget(edit)
        row_layout.addLayout(content, 1)

        arrows, up_btn, down_btn = row.make_arrows()
        row_layout.addLayout(arrows)

        self.contact_rows_container.addWidget(row)
        self.personal_fields[key] = edit
        self.contact_field_rows[key] = {"row": row, "edit": edit, "up_btn": up_btn, "down_btn": down_btn}

        row.move_requested.connect(lambda delta, k=key: self._move_contact_field(k, delta))
        row.drop_requested.connect(lambda src, after, k=key: self._on_contact_field_dropped(src, k, after))

    # ------------------------------------------------------- contact order --
    def _move_contact_field(self, key, delta):
        order = self.contact_order
        i = order.index(key)
        j = i + delta
        if not (0 <= j < len(order)):
            return
        order[i], order[j] = order[j], order[i]
        self._after_contact_order_changed()

    def _on_contact_field_dropped(self, source_row, target_key, insert_after):
        source_key = next((k for k, v in self.contact_field_rows.items() if v["row"] is source_row), None)
        if source_key is None or source_key == target_key:
            return
        order = self.contact_order
        order.remove(source_key)
        idx = order.index(target_key)
        order.insert(idx + 1 if insert_after else idx, source_key)
        self._after_contact_order_changed()

    def _after_contact_order_changed(self):
        self._rebuild_contact_rows()
        self.preview_panel.update_data(
            self._collect_data(), active_field=self._active_field,
            active_field_precise=self._active_field_precise, force=True,
        )
        self._set_status(t("status.contact_order_updated"), "ok")

    def _rebuild_contact_rows(self):
        for key in self.contact_order:
            self.contact_rows_container.removeWidget(self.contact_field_rows[key]["row"])
        for i, key in enumerate(self.contact_order):
            self.contact_rows_container.insertWidget(i, self.contact_field_rows[key]["row"])
        self._update_contact_arrows()

    def _update_contact_arrows(self):
        update_row_arrow_states([self.contact_field_rows[k] for k in self.contact_order])

    def _build_summary_page(self):
        scroll, layout = make_scroll_page()
        self.eyebrow_labels["summary"] = section_header(
            layout, f'{t("app.step")} 2', t("summary.step_title"), t("summary.step_hint"))
        self.summary_edit = QPlainTextEdit()
        self.summary_edit.setMinimumHeight(240)
        self.summary_edit._field_path_fn = lambda: "summary"
        layout.addWidget(self.summary_edit)
        layout.addStretch(1)
        self._add_page("summary", scroll)

    def _build_skills_page(self):
        scroll, layout = make_scroll_page()
        self.eyebrow_labels["skills"] = section_header(
            layout, f'{t("app.step")} 3', t("skills.step_title"), t("skills.step_hint"))
        self.skills_list = LabelValueList(t("skills.add_row"), field_prefix="skills")
        layout.addWidget(self.skills_list)
        self._add_page("skills", scroll)

    def _build_experience_page(self):
        scroll, layout = make_scroll_page()
        self.eyebrow_labels["experience"] = section_header(
            layout, f'{t("app.step")} 4', t("experience.step_title"), t("experience.step_hint"))
        self.experience_list = ExperienceList()
        layout.addWidget(self.experience_list)
        self._add_page("experience", scroll)

    def _build_education_page(self):
        scroll, layout = make_scroll_page()
        self.eyebrow_labels["education"] = section_header(
            layout, f'{t("app.step")} 5', t("education.step_title"), t("education.step_hint"))
        self.education_list = EducationList()
        layout.addWidget(self.education_list)
        self._add_page("education", scroll)

    def _build_publications_page(self):
        scroll, layout = make_scroll_page()
        self.eyebrow_labels["publications"] = section_header(
            layout, f'{t("app.step")} 6', t("publications.step_title"), t("publications.step_hint"))
        self.publications_list = PublicationList()
        layout.addWidget(self.publications_list)
        self._add_page("publications", scroll)

    def _build_certificates_page(self):
        scroll, layout = make_scroll_page()
        self.eyebrow_labels["certificates"] = section_header(
            layout, f'{t("app.step")} 7', t("certificates.step_title"), t("certificates.step_hint"))
        self.certificates_list = LabelValueList(t("certificates.add_row"), field_prefix="certificates")
        layout.addWidget(self.certificates_list)
        self._add_page("certificates", scroll)

    def _build_additional_page(self):
        scroll, layout = make_scroll_page()
        self.eyebrow_labels["additional"] = section_header(
            layout, f'{t("app.step")} 8', t("additional.step_title"), t("additional.step_hint"))
        self.additional_list = LabelValueList(t("additional.add_row"), field_prefix="additional")
        layout.addWidget(self.additional_list)
        self._add_page("additional", scroll)

    def _build_generate_page(self):
        scroll, layout = make_scroll_page()
        section_header(layout, f'{t("app.step")} 9', t("generate.step_title"), t("generate.step_hint"))

        layout.addWidget(micro_label(t("generate.live_preview")))
        layout.addSpacing(8)
        preview_hint = QLabel(t("generate.preview_hint"))
        preview_hint.setProperty("role", "hint")
        preview_hint.setWordWrap(True)
        layout.addWidget(preview_hint)
        layout.addSpacing(8)
        preview_row = QHBoxLayout()
        preview_row.setSpacing(10)
        show_preview_btn = button(t("common.hide_preview"), variant="secondary")
        show_preview_btn.clicked.connect(self._toggle_preview)
        self._preview_toggle_buttons.append(show_preview_btn)
        preview_row.addWidget(show_preview_btn)
        preview_row.addStretch(1)
        layout.addLayout(preview_row)

        layout.addSpacing(26)
        layout.addWidget(hairline())
        layout.addSpacing(22)

        layout.addWidget(micro_label(t("generate.draft")))
        layout.addSpacing(8)
        draft_row = QHBoxLayout()
        draft_row.setSpacing(10)
        save_btn = button(t("generate.save_draft"), variant="secondary")
        load_btn = button(t("generate.load_draft"), variant="secondary")
        save_btn.clicked.connect(self.save_draft)
        load_btn.clicked.connect(self.load_draft)
        draft_row.addWidget(save_btn)
        draft_row.addWidget(load_btn)
        draft_row.addStretch(1)
        layout.addLayout(draft_row)

        layout.addSpacing(26)
        layout.addWidget(hairline())
        layout.addSpacing(22)

        layout.addWidget(micro_label(t("generate.export")))
        layout.addSpacing(8)
        export_row = QHBoxLayout()
        export_row.setSpacing(10)
        docx_btn = button(t("generate.generate_docx"), variant="primary")
        pdf_btn = button(t("generate.generate_pdf"), variant="gold")
        docx_btn.clicked.connect(self.generate_docx)
        pdf_btn.clicked.connect(self.generate_pdf)
        self.gen_pdf_btn = pdf_btn
        export_row.addWidget(docx_btn)
        export_row.addWidget(pdf_btn)
        export_row.addStretch(1)
        layout.addLayout(export_row)

        layout.addStretch(1)
        self._add_page("generate", scroll)

    # --------------------------------------------------------------- nav ----
    def _select_section(self, key):
        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)
        self.stack.setCurrentIndex(self.page_index[key])
        self._refresh_nav_dots()

    def _refresh_nav_dots(self, data=None):
        data = data or self._collect_data()
        filled = {
            "personal": any(v for v in data["personal"].values()) or bool(data.get("links")),
            "summary": bool(data["summary"]),
            "skills": bool(data["skills"]),
            "experience": bool(data["experience"]),
            "education": bool(data["education"]),
            "publications": bool(data["publications"]),
            "certificates": bool(data["certificates"]),
            "additional": bool(data["additional"]),
        }
        for key, is_filled in filled.items():
            self.nav_buttons[key].set_filled(is_filled)

    # ----------------------------------------------------- section order ----
    def _move_section(self, key, delta):
        """Swap `key` with its neighbor in the given direction — everyone
        drafts a resume in a different order, so the sidebar (and the
        exported document) follows whatever order the user sets here."""
        order = self.section_order
        i = order.index(key)
        j = i + delta
        if not (0 <= j < len(order)):
            return
        order[i], order[j] = order[j], order[i]
        self._after_order_changed(t("status.section_order_updated"))

    def _on_section_dropped(self, src_key, target_key, insert_after):
        """A section's drag handle was dropped onto another section's row —
        move it to sit just before/after the drop target."""
        order = self.section_order
        if src_key == target_key or src_key not in order or target_key not in order:
            return
        order.remove(src_key)
        idx = order.index(target_key)
        order.insert(idx + 1 if insert_after else idx, src_key)
        self._after_order_changed(t("status.section_order_updated"))

    def _reset_section_order(self):
        self.section_order = list(DEFAULT_SECTION_ORDER)
        self._after_order_changed(t("status.section_order_reset"))

    def _after_order_changed(self, status_message):
        self._rebuild_sidebar_order()
        self._renumber_steps()
        self._update_arrow_states()
        self._update_reset_visibility()
        self.preview_panel.update_data(
            self._collect_data(), active_field=self._active_field,
            active_field_precise=self._active_field_precise, force=True,
        )
        self._set_status(status_message, "ok")

    def _rebuild_sidebar_order(self):
        for key in self.section_order:
            self.sidebar_layout.removeWidget(self.nav_buttons[key])
        for i, key in enumerate(self.section_order):
            self.sidebar_layout.insertWidget(self._movable_insert_index + i, self.nav_buttons[key])

    def _renumber_steps(self):
        for i, key in enumerate(self.section_order):
            step_no = i + 2  # Personal Info is always step 1
            self.nav_buttons[key].step_label.setText(f"{step_no:02d}")
            eyebrow = self.eyebrow_labels.get(key)
            if eyebrow:
                eyebrow.setText(f'{t("app.step")} {step_no}'.upper())

    def _update_arrow_states(self):
        last = len(self.section_order) - 1
        for i, key in enumerate(self.section_order):
            btn = self.nav_buttons[key]
            if btn.up_btn:
                btn.up_btn.setEnabled(i > 0)
            if btn.down_btn:
                btn.down_btn.setEnabled(i < last)

    def _update_reset_visibility(self):
        self.reset_order_btn.setVisible(self.section_order != DEFAULT_SECTION_ORDER)

    def _on_sync_tick(self):
        data = self._collect_data()
        self._refresh_nav_dots(data)
        self.preview_panel.update_data(
            data, active_field=self._active_field, active_field_precise=self._active_field_precise,
        )

    def _on_focus_changed(self, old, new):
        """Track which form field currently has focus so the live preview
        can highlight the matching part of the resume: `_active_field` is
        the whole content zone (green), `_active_field_precise` is the
        exact input box within it (yellow) — usually the same field, but
        e.g. a label/value pair in one row shares a zone while each has
        its own precise target."""
        path_fn = getattr(new, "_field_path_fn", None) if new is not None else None
        path = path_fn() if path_fn else None
        precise_fn = getattr(new, "_field_precise_fn", None) if new is not None else None
        precise = precise_fn() if precise_fn else path
        if path == self._active_field and precise == self._active_field_precise:
            return
        self._active_field = path
        self._active_field_precise = precise
        data = self._collect_data()
        self._refresh_nav_dots(data)
        self.preview_panel.update_data(data, active_field=path, active_field_precise=precise)

    # --------------------------------------------------------- data i/o -----
    def _collect_data(self):
        return {
            "personal": {k: e.text().strip() for k, e in self.personal_fields.items()},
            "links": self.links_list.get_data(),
            "section_order": list(self.section_order),
            "contact_order": list(self.contact_order),
            "language": self.language,
            "style": dict(self.style),
            "summary": self.summary_edit.toPlainText().strip(),
            "skills": self.skills_list.get_data(),
            "experience": self.experience_list.get_data(),
            "education": self.education_list.get_data(),
            "publications": self.publications_list.get_data(),
            "certificates": self.certificates_list.get_data(),
            "additional": self.additional_list.get_data(),
        }

    def _apply_data(self, data):
        self.section_order = resolve_section_order(data)
        self.contact_order = resolve_contact_order(data)

        lang = data.get("language", DEFAULT_LANGUAGE)
        if lang not in LANGUAGES:
            lang = DEFAULT_LANGUAGE
        if lang != self.language:
            # Every label in the sidebar/pages is baked in at construction
            # time, so a language change means tearing the chrome down and
            # rebuilding it — section_order/contact_order above are already
            # up to date, so the rebuild uses the right order immediately.
            self.language = lang
            set_language(lang)
            current_key = next((k for k, btn in self.nav_buttons.items() if btn.isChecked()), "personal")
            self._build_layout()
            self._select_section(current_key)
            if self._style_dialog is not None:
                # Its labels were baked in at construction too — drop it so
                # the next "Style Settings" click rebuilds it in the new
                # language rather than showing stale text.
                self._style_dialog.close()
                self._style_dialog.deleteLater()
                self._style_dialog = None

        self._rebuild_sidebar_order()
        self._renumber_steps()
        self._update_arrow_states()
        self._update_reset_visibility()

        self._rebuild_contact_rows()

        self.style = resolve_style(data)
        if self._style_dialog is not None:
            self._style_dialog.set_style(self.style)

        personal = data.get("personal", {})
        for k, e in self.personal_fields.items():
            e.setText(personal.get(k, ""))
            e.setCursorPosition(0)
        self.links_list.load_data(data.get("links", []))
        self.summary_edit.setPlainText(data.get("summary", ""))
        self.skills_list.load_data(data.get("skills", []))
        self.experience_list.load_data(data.get("experience", []))
        self.education_list.load_data(data.get("education", []))
        self.publications_list.load_data(data.get("publications", []))
        self.certificates_list.load_data(data.get("certificates", []))
        self.additional_list.load_data(data.get("additional", []))
        self._refresh_nav_dots()
        self.preview_panel.update_data(
            self._collect_data(), active_field=self._active_field,
            active_field_precise=self._active_field_precise, force=True,
        )

    def _set_status(self, text, kind=""):
        color = {"ok": theme.SUCCESS, "err": theme.DANGER}.get(kind, theme.TEXT_GRAY)
        self.status_label.setStyleSheet(f"color: {color};")
        self.status_label.setText(text)
        if kind:
            self._status_timer.start(6000)

    def save_draft(self):
        data = self._collect_data()
        default_name = (data["personal"].get("name") or "resume").strip().replace(" ", "_") + "_draft.json"
        path, _ = QFileDialog.getSaveFileName(self, t("dialog.save_draft_title"), default_name, t("filter.json_files"))
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self._set_status(t("status.draft_saved", path=path), "ok")

    def load_draft(self):
        path, _ = QFileDialog.getOpenFileName(self, t("dialog.load_draft_title"), "", t("filter.json_files"))
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:  # noqa: BLE001 — shown to the user verbatim
            QMessageBox.critical(self, t("dialog.error_loading_draft"), str(exc))
            return
        self._apply_data(data)
        self._select_section("personal")
        self._set_status(t("status.draft_loaded", path=path), "ok")

    def _validate_name(self, data):
        if not data["personal"].get("name"):
            QMessageBox.warning(self, t("dialog.missing_name_title"), t("dialog.missing_name_msg"))
            self._select_section("personal")
            return False
        return True

    def generate_docx(self):
        data = self._collect_data()
        if not self._validate_name(data):
            return
        default_name = data["personal"]["name"].strip().replace(" ", "_") + "_Resume.docx"
        path, _ = QFileDialog.getSaveFileName(
            self, t("dialog.generate_resume_title"), default_name, t("filter.word_document"))
        if not path:
            return
        try:
            build_resume(data, path)
        except Exception as exc:  # noqa: BLE001 — surfaced to the user as-is
            QMessageBox.critical(self, t("dialog.error_generating_resume"), str(exc))
            return
        self._set_status(t("status.resume_generated", path=path), "ok")
        QMessageBox.information(self, t("dialog.success_title"), t("dialog.success_msg", path=path))

    def generate_pdf(self):
        data = self._collect_data()
        if not self._validate_name(data):
            return
        default_name = data["personal"]["name"].strip().replace(" ", "_") + "_Resume.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, t("dialog.generate_resume_title"), default_name, t("filter.pdf_document"))
        if not path:
            return

        self._set_status(t("status.generating_pdf"))
        self.gen_pdf_btn.setEnabled(False)

        self._pdf_thread = PdfExportThread(data, path, self)
        self._pdf_thread.succeeded.connect(self._on_pdf_success)
        self._pdf_thread.failed.connect(self._on_pdf_error)
        self._pdf_thread.start()

    def _on_pdf_success(self, path):
        self.gen_pdf_btn.setEnabled(True)
        self._set_status(t("status.resume_generated", path=path), "ok")
        QMessageBox.information(self, t("dialog.success_title"), t("dialog.success_msg", path=path))

    def _on_pdf_error(self, message):
        self.gen_pdf_btn.setEnabled(True)
        self._set_status(t("status.pdf_failed"), "err")
        QMessageBox.critical(self, t("dialog.error_generating_pdf"), message)
