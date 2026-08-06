"""
widgets.py
Reusable UI atoms (cards, nav buttons, section headers) and the dynamic
"repeating card" list widgets that make up the form: skills/certificates
rows, project cards, experience cards, education cards, and publication
cards. Mirrors the data shapes used by docx_engine.build_resume().
"""

from PySide6.QtCore import Qt, QMimeData, Signal
from PySide6.QtGui import QColor, QDrag
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QScrollArea, QSizePolicy, QToolButton, QVBoxLayout, QWidget,
)

import theme
from i18n import t

# Stored as a language-independent key ("full_time", not "Full-time" / the
# Korean or Uzbek text) so switching the UI language never changes what's
# actually saved in a draft — only how it's displayed.
_LEGACY_EMPLOYMENT_MAP = {
    "Full-time": "full_time", "Part-time": "part_time",
    "Contract": "contract", "Freelance": "freelance",
}


def normalize_employment_type(value):
    """Map an old draft's English display-text value (from before this was
    a language-independent key) to its key; pass through anything else."""
    return _LEGACY_EMPLOYMENT_MAP.get(value, value)


def _employment_type_items():
    return [
        ("", ""),
        ("full_time", t("employment.full_time")),
        ("part_time", t("employment.part_time")),
        ("contract", t("employment.contract")),
        ("freelance", t("employment.freelance")),
    ]


def make_combo(items, current=""):
    """`items`: list of (value, display_text) pairs. `current` matches by
    value, not display text, so it's stable across language changes."""
    combo = QComboBox()
    for value, display in items:
        combo.addItem(display, value)
    idx = combo.findData(current)
    combo.setCurrentIndex(idx if idx >= 0 else 0)
    return combo


# ------------------------------------------------------------------ misc --
def apply_shadow(widget, blur=22, y=6, alpha=30):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setXOffset(0)
    effect.setYOffset(y)
    effect.setColor(QColor(16, 34, 51, alpha))
    widget.setGraphicsEffect(effect)


def refresh_style(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)


# ---------------------------------------------------- live-preview linking --
# Each editable widget can carry a `_field_path_fn` attribute — a zero-arg
# callable that resolves to the dotted field id (e.g. "experience.0.title")
# it currently corresponds to in the rendered preview, or None while the
# entry it belongs to is still blank (and so isn't rendered at all). The
# path is resolved lazily at focus-time (not stored as a fixed string)
# because a row/card's position can shift as sibling rows are added or
# removed above it.
def _visible_index(entries, target, is_visible):
    """Index of `target` among `entries` that satisfy `is_visible`, matching
    the same filtering each list's get_data() applies before rendering.
    Returns None if `target` itself isn't currently visible."""
    if not is_visible(target):
        return None
    idx = 0
    for e in entries:
        if e is target:
            return idx
        if is_visible(e):
            idx += 1
    return None


def _lv_row_visible(r):
    return bool(r["label"].text().strip() or r["value"].text().strip())


def _job_visible(c):
    return bool(c["title"].text().strip() or c["company"].text().strip())


def _edu_visible(c):
    return bool(c["degree"].text().strip())


def _pub_visible(c):
    return bool(c["title"].text().strip() or c["detail"].text().strip())


def _proj_visible(p):
    if p["name"].text().strip() or p["url"].text().strip():
        return True
    return any(b.strip() for b in p["bullets"].toPlainText().split("\n"))


def micro_label(text):
    lbl = QLabel(text.upper())
    lbl.setProperty("role", "microLabel")
    lbl.setWordWrap(True)
    return lbl


def hairline():
    line = QFrame()
    line.setProperty("role", "hairline")
    line.setFrameShape(QFrame.Shape.NoFrame)
    return line


def button(text, variant="secondary", small=False):
    btn = QPushButton(text)
    btn.setProperty("variant", variant)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if small:
        btn.setFixedHeight(28)
    return btn


def remove_icon_button(tooltip=None):
    btn = QPushButton("✕")
    btn.setProperty("variant", "iconGhost")
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFixedSize(26, 26)
    btn.setToolTip(tooltip if tooltip is not None else t("common.remove"))
    return btn


def add_field(layout, label_text, widget, gap_before=12):
    if gap_before:
        layout.addSpacing(gap_before)
    layout.addWidget(micro_label(label_text))
    layout.addSpacing(4)
    layout.addWidget(widget)


def make_line_edit(text="", bold=False, placeholder=""):
    e = QLineEdit(text)
    if placeholder:
        e.setPlaceholderText(placeholder)
    f = e.font()
    f.setBold(bold)
    e.setFont(f)
    e.setCursorPosition(0)
    return e


def section_header(layout, eyebrow, title, hint):
    """Returns the eyebrow QLabel (e.g. "STEP 3") so callers whose step
    number can shift — because the user reordered sections — can update it
    later without rebuilding the whole page."""
    eyebrow_lbl = QLabel(eyebrow.upper())
    eyebrow_lbl.setProperty("role", "eyebrow")
    layout.addWidget(eyebrow_lbl)

    title_lbl = QLabel(title)
    title_lbl.setProperty("role", "sectionTitle")
    title_lbl.setFont(theme.serif_font(21, weight=700))
    layout.addWidget(title_lbl)

    hint_lbl = QLabel(hint)
    hint_lbl.setProperty("role", "hint")
    hint_lbl.setWordWrap(True)
    layout.addWidget(hint_lbl)

    layout.addSpacing(14)
    layout.addWidget(hairline())
    layout.addSpacing(22)

    return eyebrow_lbl


def make_scroll_page():
    """A vertically-scrolling page. Returns (scroll_area, body_layout)."""
    scroll = QScrollArea()
    scroll.setObjectName("FormScroll")
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    body = QWidget()
    body_layout = QVBoxLayout(body)
    body_layout.setContentsMargins(40, 32, 40, 40)
    body_layout.setSpacing(0)
    scroll.setWidget(body)
    return scroll, body_layout


def card_frame(kind="main", reorderable=False):
    frame = ReorderableRow() if reorderable else QFrame()
    frame.setObjectName("Card" if kind == "main" else "SubCard")
    if kind == "main":
        apply_shadow(frame, blur=26, y=7, alpha=26)
    else:
        apply_shadow(frame, blur=14, y=3, alpha=16)
    return frame


def badge_label(text, kind="main"):
    lbl = QLabel(str(text))
    lbl.setObjectName("CardBadge" if kind == "main" else "SubCardBadge")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    if kind == "main":
        lbl.setFixedSize(26, 26)
    else:
        lbl.setFixedSize(20, 20)
    return lbl


# ------------------------------------------------------------- nav d&d ---
_NAV_DRAG_MIME = "application/x-resumebuilder-navsection"
_DRAG_THRESHOLD = 8


class _NavDragHandle(QLabel):
    """Small grip on a reorderable NavButton — press it and drag with the
    mouse to move that section. Only this handle initiates a drag; the rest
    of the button keeps behaving like a normal click-to-navigate button."""

    def __init__(self, nav_button, parent=None):
        super().__init__("⣿", parent)
        self._nav_button = nav_button
        self.setObjectName("NavDragHandle")
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setToolTip(t("common.drag_reorder_section"))
        self.setFixedWidth(16)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._press_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.position().toPoint()
        event.accept()

    def mouseMoveEvent(self, event):
        if self._press_pos is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            moved = event.position().toPoint() - self._press_pos
            if moved.manhattanLength() >= _DRAG_THRESHOLD:
                self._start_drag()
        event.accept()

    def mouseReleaseEvent(self, event):
        self._press_pos = None
        event.accept()

    def _start_drag(self):
        press_pos, self._press_pos = self._press_pos, None
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(_NAV_DRAG_MIME, self._nav_button.section_key.encode("utf-8"))
        drag.setMimeData(mime)
        drag.setPixmap(self._nav_button.grab())
        drag.setHotSpot(self.mapTo(self._nav_button, press_pos))
        drag.exec(Qt.DropAction.MoveAction)


# =================================================================== nav ==
class NavButton(QPushButton):
    """A sidebar navigation entry: step number + label + a completion dot
    that lights up gold once that section has content. When `movable` is
    set, it also carries a drag handle plus a pair of tiny up/down reorder
    buttons — everyone drafts a resume in a different order, so the middle
    sections (Summary through Additional Info) can be rearranged to match,
    either by dragging with the mouse or by clicking the arrows."""

    move_requested = Signal(int)  # -1 = move up, +1 = move down
    drop_requested = Signal(str, str, bool)  # source_key, target_key, insert_after

    def __init__(self, step_no, text, key=None, movable=False, parent=None):
        super().__init__(parent)
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(46)
        self.section_key = key
        self.movable = movable

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 8 if movable else 15, 0)
        layout.setSpacing(8 if movable else 10)

        self.step_label = QLabel(step_no)
        self.step_label.setObjectName("NavStep")
        self.step_label.setFixedWidth(20)
        self.step_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.text_label = QLabel(text)
        self.text_label.setObjectName("NavText")
        self.text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.dot_label = QLabel("●")
        self.dot_label.setObjectName("NavDot")
        self.dot_label.setFixedWidth(14)
        self.dot_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.dot_label.setProperty("filled", "false")

        layout.addWidget(self.step_label)
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.dot_label)

        self.up_btn = None
        self.down_btn = None
        if movable:
            self.setAcceptDrops(True)

            layout.addWidget(_NavDragHandle(self))

            arrows = QVBoxLayout()
            arrows.setContentsMargins(0, 0, 0, 0)
            arrows.setSpacing(0)

            self.up_btn = QToolButton()
            self.up_btn.setObjectName("NavReorderBtn")
            self.up_btn.setText("▲")
            self.up_btn.setToolTip(t("common.move_section_up"))
            self.up_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.up_btn.setFixedSize(18, 14)
            self.up_btn.clicked.connect(lambda: self.move_requested.emit(-1))

            self.down_btn = QToolButton()
            self.down_btn.setObjectName("NavReorderBtn")
            self.down_btn.setText("▼")
            self.down_btn.setToolTip(t("common.move_section_down"))
            self.down_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.down_btn.setFixedSize(18, 14)
            self.down_btn.clicked.connect(lambda: self.move_requested.emit(1))

            arrows.addWidget(self.up_btn)
            arrows.addWidget(self.down_btn)
            layout.addLayout(arrows)

        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked):
        self.step_label.setProperty("active", "true" if checked else "false")
        self.text_label.setProperty("active", "true" if checked else "false")
        refresh_style(self.step_label)
        refresh_style(self.text_label)

    # ---- drop target: another NavButton's drag handle dropping onto us ----
    def dragEnterEvent(self, event):
        if self.movable and event.mimeData().hasFormat(_NAV_DRAG_MIME):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if not (self.movable and event.mimeData().hasFormat(_NAV_DRAG_MIME)):
            event.ignore()
            return
        indicator = "before" if event.position().y() < self.height() / 2 else "after"
        if self.property("dropIndicator") != indicator:
            self.setProperty("dropIndicator", indicator)
            refresh_style(self)
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        if self.property("dropIndicator"):
            self.setProperty("dropIndicator", None)
            refresh_style(self)

    def dropEvent(self, event):
        if not (self.movable and event.mimeData().hasFormat(_NAV_DRAG_MIME)):
            event.ignore()
            return
        src_key = bytes(event.mimeData().data(_NAV_DRAG_MIME)).decode("utf-8")
        insert_after = self.property("dropIndicator") == "after"
        self.setProperty("dropIndicator", None)
        refresh_style(self)
        event.acceptProposedAction()
        if src_key and src_key != self.section_key:
            self.drop_requested.emit(src_key, self.section_key, insert_after)

    def set_filled(self, filled):
        self.dot_label.setProperty("filled", "true" if filled else "false")
        refresh_style(self.dot_label)


# ---------------------------------------------------------- reorderable rows --
# Generic drag-and-drop reordering for rows *within* a single list — skill/
# certificate/additional-info rows, and the Location/Phone/Email/Visa fields
# in Personal Info. (Separate machinery from the nav sidebar's above: same
# idea, but these rows move within their own container rather than the
# fixed sidebar layout.)
_ROW_DRAG_MIME = "application/x-resumebuilder-row"

# Which ReorderableRow is currently being dragged, if any. Qt's drag-and-drop
# is inherently single-drag-at-a-time per application and QDrag.exec() blocks
# until the drag ends, so a module-level slot is safe here — and simpler
# (and easier to test) than relying on QDropEvent.source().
_current_drag_row = None


class RowDragHandle(QLabel):
    """Small grip on a ReorderableRow — press it and drag with the mouse to
    move that row among its siblings."""

    def __init__(self, owner, parent=None):
        super().__init__("⣿", parent)
        self.owner = owner
        self.setObjectName("RowDragHandle")
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setToolTip(t("common.drag_reorder"))
        self.setFixedWidth(16)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._press_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.position().toPoint()
        event.accept()

    def mouseMoveEvent(self, event):
        if self._press_pos is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            moved = event.position().toPoint() - self._press_pos
            if moved.manhattanLength() >= _DRAG_THRESHOLD:
                self._start_drag()
        event.accept()

    def mouseReleaseEvent(self, event):
        self._press_pos = None
        event.accept()

    def _start_drag(self):
        global _current_drag_row
        press_pos, self._press_pos = self._press_pos, None
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(_ROW_DRAG_MIME, b"1")
        drag.setMimeData(mime)
        drag.setPixmap(self.owner.grab())
        drag.setHotSpot(self.mapTo(self.owner, press_pos))
        _current_drag_row = self.owner
        try:
            drag.exec(Qt.DropAction.MoveAction)
        finally:
            _current_drag_row = None


class ReorderableRow(QFrame):
    """A row that can be dragged (via a RowDragHandle placed in its own
    layout by the caller) to reorder itself among sibling ReorderableRows
    in the same container, and that accepts drops from siblings to decide
    where they land. The caller builds whatever content the row holds and
    wires `move_requested` / `drop_requested` to its own reorder logic —
    this class only owns the drag-and-drop mechanics."""

    move_requested = Signal(int)             # -1 = up, +1 = down
    drop_requested = Signal(QFrame, bool)     # dropped_row, insert_after

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def make_handle(self):
        return RowDragHandle(self)

    def make_arrows(self):
        """A small ▲/▼ pair wired to move_requested — returns the layout to
        place plus the two buttons, so the caller can manage their enabled
        state (disabled at the top/bottom of the list)."""
        arrows = QVBoxLayout()
        arrows.setContentsMargins(0, 0, 0, 0)
        arrows.setSpacing(0)

        up_btn = QToolButton()
        up_btn.setObjectName("RowReorderBtn")
        up_btn.setText("▲")
        up_btn.setToolTip(t("common.move_up"))
        up_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        up_btn.setFixedSize(18, 14)
        up_btn.clicked.connect(lambda: self.move_requested.emit(-1))

        down_btn = QToolButton()
        down_btn.setObjectName("RowReorderBtn")
        down_btn.setText("▼")
        down_btn.setToolTip(t("common.move_down"))
        down_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        down_btn.setFixedSize(18, 14)
        down_btn.clicked.connect(lambda: self.move_requested.emit(1))

        arrows.addWidget(up_btn)
        arrows.addWidget(down_btn)
        return arrows, up_btn, down_btn

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(_ROW_DRAG_MIME):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if not event.mimeData().hasFormat(_ROW_DRAG_MIME):
            event.ignore()
            return
        indicator = "before" if event.position().y() < self.height() / 2 else "after"
        if self.property("dropIndicator") != indicator:
            self.setProperty("dropIndicator", indicator)
            refresh_style(self)
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        if self.property("dropIndicator"):
            self.setProperty("dropIndicator", None)
            refresh_style(self)

    def dropEvent(self, event):
        if not event.mimeData().hasFormat(_ROW_DRAG_MIME):
            event.ignore()
            return
        insert_after = self.property("dropIndicator") == "after"
        self.setProperty("dropIndicator", None)
        refresh_style(self)
        event.acceptProposedAction()
        if isinstance(_current_drag_row, ReorderableRow) and _current_drag_row is not self:
            self.drop_requested.emit(_current_drag_row, insert_after)


def update_row_arrow_states(rows, up_key="up_btn", down_key="down_btn"):
    """Shared by every reorderable row list: disable ▲ on the first row and
    ▼ on the last. `rows` is a list of dicts each holding the two buttons."""
    last = len(rows) - 1
    for i, row in enumerate(rows):
        row[up_key].setEnabled(i > 0)
        row[down_key].setEnabled(i < last)


# ============================================================ label/value ==
class LabelValueList(QWidget):
    """Dynamic list of (label, value) rows — used for Skills, Certificates,
    and Additional Info."""

    def __init__(self, add_text=None, field_prefix="", parent=None,
                 label_placeholder=None, value_placeholder=None):
        super().__init__(parent)
        self.rows = []
        self.field_prefix = field_prefix
        self.label_placeholder = label_placeholder if label_placeholder is not None else t("common.label_placeholder")
        self.value_placeholder = value_placeholder if value_placeholder is not None else t("common.details_placeholder")
        add_text = add_text if add_text is not None else t("common.add_row")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        self.container = QVBoxLayout()
        self.container.setSpacing(8)
        outer.addLayout(self.container)

        add_btn = button(add_text, variant="ghost")
        add_btn.clicked.connect(lambda: self.add_row())
        row_wrap = QHBoxLayout()
        row_wrap.addWidget(add_btn)
        row_wrap.addStretch(1)
        outer.addSpacing(6)
        outer.addLayout(row_wrap)
        outer.addStretch(1)

    def add_row(self, label="", value=""):
        frame = ReorderableRow()
        frame.setObjectName("Row")
        row_layout = QHBoxLayout(frame)
        row_layout.setContentsMargins(10, 9, 9, 9)
        row_layout.setSpacing(8)

        row_layout.addWidget(frame.make_handle())

        label_edit = make_line_edit(label, bold=True, placeholder=self.label_placeholder)
        label_edit.setFixedWidth(220)
        value_edit = make_line_edit(value, placeholder=self.value_placeholder)

        row_layout.addWidget(label_edit)
        row_layout.addWidget(value_edit, 1)

        arrows, up_btn, down_btn = frame.make_arrows()
        row_layout.addLayout(arrows)

        remove_btn = remove_icon_button(t("common.remove_row"))
        row_layout.addWidget(remove_btn)

        self.container.addWidget(frame)
        entry = {
            "frame": frame, "label": label_edit, "value": value_edit,
            "up_btn": up_btn, "down_btn": down_btn,
        }

        if self.field_prefix:
            def _row_path(entry=entry):
                idx = _visible_index(self.rows, entry, _lv_row_visible)
                return f"{self.field_prefix}.{idx}" if idx is not None else None

            def _row_precise_path(entry, suffix):
                def fn():
                    idx = _visible_index(self.rows, entry, _lv_row_visible)
                    return f"{self.field_prefix}.{idx}.{suffix}" if idx is not None else None
                return fn

            label_edit._field_path_fn = _row_path
            value_edit._field_path_fn = _row_path
            # The whole row shares one green content-zone, but the label and
            # value are each their own yellow "exact input box" target.
            label_edit._field_precise_fn = _row_precise_path(entry, "label")
            value_edit._field_precise_fn = _row_precise_path(entry, "value")

        remove_btn.clicked.connect(lambda: self.remove_row(entry))
        frame.move_requested.connect(lambda delta, e=entry: self._move_row(e, delta))
        frame.drop_requested.connect(lambda src, after, tgt=frame: self._on_row_dropped(src, tgt, after))
        self.rows.append(entry)
        self._update_row_arrows()
        return entry

    def remove_row(self, entry):
        entry["frame"].setParent(None)
        entry["frame"].deleteLater()
        self.rows.remove(entry)
        self._update_row_arrows()

    def _move_row(self, entry, delta):
        i = self.rows.index(entry)
        j = i + delta
        if not (0 <= j < len(self.rows)):
            return
        self.rows[i], self.rows[j] = self.rows[j], self.rows[i]
        self._rebuild_row_order()

    def _on_row_dropped(self, source_frame, target_frame, insert_after):
        src_entry = next((r for r in self.rows if r["frame"] is source_frame), None)
        tgt_entry = next((r for r in self.rows if r["frame"] is target_frame), None)
        if src_entry is None or tgt_entry is None or src_entry is tgt_entry:
            return
        self.rows.remove(src_entry)
        idx = self.rows.index(tgt_entry)
        self.rows.insert(idx + 1 if insert_after else idx, src_entry)
        self._rebuild_row_order()

    def _rebuild_row_order(self):
        for entry in self.rows:
            self.container.removeWidget(entry["frame"])
        for i, entry in enumerate(self.rows):
            self.container.insertWidget(i, entry["frame"])
        self._update_row_arrows()

    def _update_row_arrows(self):
        update_row_arrow_states(self.rows)

    def get_data(self):
        return [
            {"label": r["label"].text().strip(), "value": r["value"].text().strip()}
            for r in self.rows if r["label"].text().strip() or r["value"].text().strip()
        ]

    def load_data(self, items):
        for r in list(self.rows):
            self.remove_row(r)
        for item in items:
            self.add_row(item.get("label", ""), item.get("value", ""))


# ================================================================ projects ==
class ProjectList(QWidget):
    """Nested inside a company card: one or more named projects, each with
    its own bullet points."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []
        self.company_index_fn = None  # set by the owning ExperienceList entry

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)

        self.container = QVBoxLayout()
        self.container.setSpacing(10)
        outer.addLayout(self.container)

        add_btn = button(t("experience.add_project"), variant="ghostSmall", small=True)
        add_btn.clicked.connect(lambda: self.add_card())
        row = QHBoxLayout()
        row.addWidget(add_btn)
        row.addStretch(1)
        outer.addLayout(row)

    def add_card(self, name="", bullets="", url=""):
        frame = card_frame("sub", reorderable=True)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(0)

        top_row = QHBoxLayout()
        top_row.addWidget(frame.make_handle())
        top_row.addStretch(1)
        arrows, up_btn, down_btn = frame.make_arrows()
        top_row.addLayout(arrows)
        layout.addLayout(top_row)
        layout.addSpacing(6)

        name_edit = make_line_edit(name, bold=True)
        add_field(layout, t("experience.project_name"), name_edit, gap_before=0)

        url_edit = make_line_edit(url, placeholder=t("common.url_placeholder"))
        add_field(layout, t("experience.project_link"), url_edit)

        bullets_edit = QPlainTextEdit()
        bullets_edit.setPlainText(bullets)
        bullets_edit.setFixedHeight(84)
        bullets_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        add_field(layout, t("experience.bullets"), bullets_edit)

        remove_btn = button(t("experience.remove_project"), variant="danger", small=True)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(remove_btn)
        layout.addSpacing(10)
        layout.addLayout(btn_row)

        self.container.addWidget(frame)
        entry = {
            "frame": frame, "name": name_edit, "url": url_edit, "bullets": bullets_edit,
            "up_btn": up_btn, "down_btn": down_btn,
        }

        def _proj_path(entry, suffix):
            def fn():
                company_idx = self.company_index_fn() if self.company_index_fn else None
                if company_idx is None:
                    return None
                proj_idx = _visible_index(self.cards, entry, _proj_visible)
                if proj_idx is None:
                    return None
                return f"experience.{company_idx}.projects.{proj_idx}.{suffix}"
            return fn

        name_edit._field_path_fn = _proj_path(entry, "heading")
        url_edit._field_path_fn = _proj_path(entry, "heading")
        bullets_edit._field_path_fn = _proj_path(entry, "bullets")

        remove_btn.clicked.connect(lambda: self.remove_card(entry))
        frame.move_requested.connect(lambda delta, e=entry: self._move_card(e, delta))
        frame.drop_requested.connect(lambda src, after, tgt=frame: self._on_card_dropped(src, tgt, after))
        self.cards.append(entry)
        self._update_card_arrows()
        return entry

    def remove_card(self, entry):
        entry["frame"].setParent(None)
        entry["frame"].deleteLater()
        self.cards.remove(entry)
        self._update_card_arrows()

    def _move_card(self, entry, delta):
        i = self.cards.index(entry)
        j = i + delta
        if not (0 <= j < len(self.cards)):
            return
        self.cards[i], self.cards[j] = self.cards[j], self.cards[i]
        self._rebuild_card_order()

    def _on_card_dropped(self, source_frame, target_frame, insert_after):
        src = next((c for c in self.cards if c["frame"] is source_frame), None)
        tgt = next((c for c in self.cards if c["frame"] is target_frame), None)
        if src is None or tgt is None or src is tgt:
            return
        self.cards.remove(src)
        idx = self.cards.index(tgt)
        self.cards.insert(idx + 1 if insert_after else idx, src)
        self._rebuild_card_order()

    def _rebuild_card_order(self):
        for entry in self.cards:
            self.container.removeWidget(entry["frame"])
        for i, entry in enumerate(self.cards):
            self.container.insertWidget(i, entry["frame"])
        self._update_card_arrows()

    def _update_card_arrows(self):
        update_row_arrow_states(self.cards)

    def get_data(self):
        result = []
        for c in self.cards:
            name = c["name"].text().strip()
            url = c["url"].text().strip()
            bullets = c["bullets"].toPlainText().split("\n")
            if name or url or any(b.strip() for b in bullets):
                result.append({"name": name, "url": url, "bullets": bullets})
        return result

    def load_data(self, items):
        for c in list(self.cards):
            self.remove_card(c)
        for item in items:
            self.add_card(item.get("name", ""), "\n".join(item.get("bullets", [])), item.get("url", ""))


# =============================================================== experience ==
class ExperienceList(QWidget):
    """Dynamic list of company cards. Each company holds one or more
    project cards."""

    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        self.container = QVBoxLayout()
        self.container.setSpacing(16)
        outer.addLayout(self.container)

        add_btn = button(t("experience.add_company"), variant="primary")
        add_btn.clicked.connect(lambda: self.add_card())
        row = QHBoxLayout()
        row.addWidget(add_btn)
        row.addStretch(1)
        outer.addSpacing(4)
        outer.addLayout(row)
        outer.addStretch(1)

    def add_card(self, title="", company="", start_date="", end_date="", projects=None,
                 company_url="", employment_type=""):
        frame = card_frame("main")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(0)

        top_row = QHBoxLayout()
        badge = badge_label(len(self.cards) + 1, "main")
        top_row.addWidget(badge)
        top_row.addStretch(1)
        remove_btn = button(t("experience.remove_company"), variant="danger", small=True)
        top_row.addWidget(remove_btn)
        layout.addLayout(top_row)
        layout.addSpacing(12)

        fields_row = QHBoxLayout()
        fields_row.setSpacing(14)

        title_box = QVBoxLayout()
        title_box.addWidget(micro_label(t("experience.job_title")))
        title_edit = make_line_edit(title, bold=True)
        title_box.addWidget(title_edit)

        company_box = QVBoxLayout()
        company_box.addWidget(micro_label(t("experience.company")))
        company_edit = make_line_edit(company, bold=True)
        company_box.addWidget(company_edit)

        employment_box = QVBoxLayout()
        employment_box.addWidget(micro_label(t("experience.employment_type")))
        employment_edit = make_combo(_employment_type_items(), normalize_employment_type(employment_type))
        employment_box.addWidget(employment_edit)

        fields_row.addLayout(title_box, 2)
        fields_row.addLayout(company_box, 2)
        fields_row.addLayout(employment_box, 1)
        layout.addLayout(fields_row)

        layout.addSpacing(14)
        dates_row = QHBoxLayout()
        dates_row.setSpacing(14)

        start_box = QVBoxLayout()
        start_box.addWidget(micro_label(t("experience.start_date")))
        start_date_edit = make_line_edit(start_date, placeholder=t("experience.start_date_placeholder"))
        start_box.addWidget(start_date_edit)

        end_box = QVBoxLayout()
        end_box.addWidget(micro_label(t("experience.end_date")))
        end_date_edit = make_line_edit(end_date, placeholder=t("experience.end_date_placeholder"))
        end_box.addWidget(end_date_edit)

        dates_row.addLayout(start_box, 1)
        dates_row.addLayout(end_box, 1)
        layout.addLayout(dates_row)

        company_url_edit = make_line_edit(company_url, placeholder=t("common.url_placeholder"))
        add_field(layout, t("experience.company_link"), company_url_edit)

        layout.addSpacing(14)
        layout.addWidget(hairline())
        layout.addSpacing(12)
        layout.addWidget(micro_label(t("experience.projects_heading")))
        layout.addSpacing(6)

        projects_list = ProjectList()
        layout.addWidget(projects_list)
        if projects:
            projects_list.load_data(projects)
        else:
            projects_list.add_card()

        self.container.addWidget(frame)
        entry = {
            "frame": frame, "badge": badge, "title": title_edit, "company": company_edit,
            "start_date": start_date_edit, "end_date": end_date_edit,
            "employment_type": employment_edit,
            "company_url": company_url_edit, "projects": projects_list,
        }

        def _exp_path(entry, suffix):
            def fn():
                idx = _visible_index(self.cards, entry, _job_visible)
                return f"experience.{idx}.{suffix}" if idx is not None else None
            return fn

        title_edit._field_path_fn = _exp_path(entry, "title")
        company_edit._field_path_fn = _exp_path(entry, "company")
        company_url_edit._field_path_fn = _exp_path(entry, "company")
        start_date_edit._field_path_fn = _exp_path(entry, "dates")
        end_date_edit._field_path_fn = _exp_path(entry, "dates")
        # The whole dates line shares one green content-zone, but start and
        # end are each their own yellow "exact input box" target.
        start_date_edit._field_precise_fn = _exp_path(entry, "dates.start")
        end_date_edit._field_precise_fn = _exp_path(entry, "dates.end")
        employment_edit._field_path_fn = _exp_path(entry, "employment_type")
        employment_edit._field_precise_fn = _exp_path(entry, "employment_type")
        projects_list.company_index_fn = lambda: _visible_index(self.cards, entry, _job_visible)

        remove_btn.clicked.connect(lambda: self.remove_card(entry))
        self.cards.append(entry)
        return entry

    def remove_card(self, entry):
        entry["frame"].setParent(None)
        entry["frame"].deleteLater()
        self.cards.remove(entry)
        self._renumber()

    def _renumber(self):
        for i, c in enumerate(self.cards):
            c["badge"].setText(str(i + 1))

    def get_data(self):
        result = []
        for c in self.cards:
            title = c["title"].text().strip()
            company = c["company"].text().strip()
            if title or company:
                result.append({
                    "title": title,
                    "company": company,
                    "company_url": c["company_url"].text().strip(),
                    "start_date": c["start_date"].text().strip(),
                    "end_date": c["end_date"].text().strip(),
                    "employment_type": c["employment_type"].currentData() or "",
                    "projects": c["projects"].get_data(),
                })
        return result

    def load_data(self, items):
        for c in list(self.cards):
            self.remove_card(c)
        for item in items:
            start_date = item.get("start_date", "")
            end_date = item.get("end_date", "")
            if not start_date and not end_date and item.get("dates"):
                # Older drafts stored a single combined "dates" string.
                legacy = item["dates"].strip()
                for sep in (" – ", " - ", "–", "-"):
                    if sep in legacy:
                        start_date, end_date = (p.strip() for p in legacy.split(sep, 1))
                        break
                else:
                    start_date = legacy
            self.add_card(item.get("title", ""), item.get("company", ""),
                          start_date, end_date, item.get("projects", []),
                          item.get("company_url", ""), item.get("employment_type", ""))


# ================================================================ education ==
class EducationList(QWidget):
    """Dynamic list of education entries: degree / school / meta line."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(14)

        self.container = QVBoxLayout()
        self.container.setSpacing(14)
        outer.addLayout(self.container)

        add_btn = button(t("education.add"), variant="primary")
        add_btn.clicked.connect(lambda: self.add_card())
        row = QHBoxLayout()
        row.addWidget(add_btn)
        row.addStretch(1)
        outer.addSpacing(4)
        outer.addLayout(row)
        outer.addStretch(1)

    def add_card(self, degree="", school="", meta="", school_url=""):
        frame = card_frame("main")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(0)

        top_row = QHBoxLayout()
        badge = badge_label(len(self.cards) + 1, "main")
        top_row.addWidget(badge)
        top_row.addStretch(1)
        remove_btn = button(t("common.remove"), variant="danger", small=True)
        top_row.addWidget(remove_btn)
        layout.addLayout(top_row)

        degree_edit = make_line_edit(degree, bold=True)
        add_field(layout, t("education.degree"), degree_edit, gap_before=10)

        school_edit = make_line_edit(school)
        add_field(layout, t("education.school"), school_edit)

        school_url_edit = make_line_edit(school_url, placeholder=t("common.url_placeholder"))
        add_field(layout, t("education.school_link"), school_url_edit)

        meta_edit = make_line_edit(meta)
        add_field(layout, t("education.meta"), meta_edit)

        self.container.addWidget(frame)
        entry = {"frame": frame, "badge": badge, "degree": degree_edit, "school": school_edit,
                 "meta": meta_edit, "school_url": school_url_edit}

        def _edu_path(entry, suffix):
            def fn():
                idx = _visible_index(self.cards, entry, _edu_visible)
                return f"education.{idx}.{suffix}" if idx is not None else None
            return fn

        degree_edit._field_path_fn = _edu_path(entry, "line")
        school_edit._field_path_fn = _edu_path(entry, "line")
        school_url_edit._field_path_fn = _edu_path(entry, "line")
        meta_edit._field_path_fn = _edu_path(entry, "meta")
        # Degree and school share one green content-zone (they're one line
        # in the preview), but each is its own yellow "exact input box"
        # target; the school link URL doesn't have its own visible text, so
        # it shares the school name's precise target.
        degree_edit._field_precise_fn = _edu_path(entry, "degree")
        school_edit._field_precise_fn = _edu_path(entry, "school")
        school_url_edit._field_precise_fn = _edu_path(entry, "school")

        remove_btn.clicked.connect(lambda: self.remove_card(entry))
        self.cards.append(entry)
        return entry

    def remove_card(self, entry):
        entry["frame"].setParent(None)
        entry["frame"].deleteLater()
        self.cards.remove(entry)
        self._renumber()

    def _renumber(self):
        for i, c in enumerate(self.cards):
            c["badge"].setText(str(i + 1))

    def get_data(self):
        result = []
        for c in self.cards:
            degree = c["degree"].text().strip()
            if degree:
                result.append({
                    "degree": degree,
                    "school": c["school"].text().strip(),
                    "school_url": c["school_url"].text().strip(),
                    "meta": c["meta"].text().strip(),
                })
        return result

    def load_data(self, items):
        for c in list(self.cards):
            self.remove_card(c)
        for item in items:
            self.add_card(item.get("degree", ""), item.get("school", ""),
                           item.get("meta", ""), item.get("school_url", ""))


# ============================================================= publications ==
class PublicationList(QWidget):
    """Dynamic list of publication / patent cards: title + detail
    (venue, date, patent no.)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(14)

        self.container = QVBoxLayout()
        self.container.setSpacing(14)
        outer.addLayout(self.container)

        add_btn = button(t("publications.add"), variant="primary")
        add_btn.clicked.connect(lambda: self.add_card())
        row = QHBoxLayout()
        row.addWidget(add_btn)
        row.addStretch(1)
        outer.addSpacing(4)
        outer.addLayout(row)
        outer.addStretch(1)

    def add_card(self, title="", detail=""):
        frame = card_frame("main")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(0)

        top_row = QHBoxLayout()
        badge = badge_label(len(self.cards) + 1, "main")
        top_row.addWidget(badge)
        top_row.addStretch(1)
        remove_btn = button(t("common.remove"), variant="danger", small=True)
        top_row.addWidget(remove_btn)
        layout.addLayout(top_row)

        title_edit = make_line_edit(title, bold=True)
        add_field(layout, t("publications.title"), title_edit, gap_before=10)

        detail_edit = make_line_edit(detail)
        add_field(layout, t("publications.detail"), detail_edit)

        self.container.addWidget(frame)
        entry = {"frame": frame, "badge": badge, "title": title_edit, "detail": detail_edit}

        def _pub_path(entry, suffix):
            def fn():
                idx = _visible_index(self.cards, entry, _pub_visible)
                return f"publications.{idx}.{suffix}" if idx is not None else None
            return fn

        title_edit._field_path_fn = _pub_path(entry, "title")
        detail_edit._field_path_fn = _pub_path(entry, "detail")

        remove_btn.clicked.connect(lambda: self.remove_card(entry))
        self.cards.append(entry)
        return entry

    def remove_card(self, entry):
        entry["frame"].setParent(None)
        entry["frame"].deleteLater()
        self.cards.remove(entry)
        self._renumber()

    def _renumber(self):
        for i, c in enumerate(self.cards):
            c["badge"].setText(str(i + 1))

    def get_data(self):
        result = []
        for c in self.cards:
            title = c["title"].text().strip()
            detail = c["detail"].text().strip()
            if title or detail:
                result.append({"title": title, "detail": detail})
        return result

    def load_data(self, items):
        for c in list(self.cards):
            self.remove_card(c)
        for item in items:
            if isinstance(item, dict):
                self.add_card(item.get("title", ""), item.get("detail", ""))
            else:
                self.add_card(str(item), "")
