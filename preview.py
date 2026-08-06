"""
preview.py
Renders the resume data as an HTML "sheet" — the same navy/brass palette
and type-scale as docx_engine.py's .docx output — and shows it live in a
QWebEngineView, so the app can offer something neither of the earlier
editions had: a real-time, on-page preview of the finished resume.
"""

import html
import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractSpinBox, QFrame, QHBoxLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)
from PySide6.QtWebEngineWidgets import QWebEngineView

import theme
from docx_engine import (
    format_date_range, format_employment_type, resolve_contact_order, resolve_section_order,
)
from i18n import DEFAULT_LANGUAGE, t
from resume_style import css_font_stack, resolve_style


def build_page_css(style):
    """The resume sheet's CSS, parametrized by the resolved style — same
    colors/sizes/font as docx_engine.build_resume() so the live preview
    never drifts from what actually gets exported."""
    return f"""
:root {{
    --accent: {style['accent_color']};
    --accent-soft: {style['accent_soft_color']};
    --gold: {style['highlight_color']};
    --muted: {style['muted_color']};
    --text: {style['text_color']};
    --page-bg: {style['background_color']};
    --line: #C9D2D8;
    --size-name: {style['size_name']}pt;
    --size-title: {style['size_title']}pt;
    --size-heading: {style['size_heading']}pt;
    --size-body: {style['size_body']}pt;
    --size-meta: {style['size_meta']}pt;
}}
* {{ box-sizing: border-box; }}
html, body {{
    margin: 0;
    background: #DDE2E7;
    font-family: {css_font_stack(style['font_family'])};
}}
body {{
    display: flex;
    justify-content: center;
    padding: 26px 18px 60px;
}}
.sheet {{
    width: 8.5in;
    min-height: 11in;
    padding: 0.65in;
    background: var(--page-bg);
    color: var(--text);
    font-size: var(--size-body);
    line-height: 1.38;
    box-shadow: 0 8px 30px rgba(15, 30, 45, 0.22);
}}
.sheet-empty {{
    color: var(--muted);
    font-style: italic;
    text-align: center;
    margin-top: 2.2in;
    font-size: 12pt;
}}
.sheet-name {{
    text-align: center;
    font-size: var(--size-name);
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--accent);
    margin-bottom: 2pt;
}}
.sheet-title {{
    text-align: center;
    font-size: var(--size-title);
    font-style: italic;
    color: var(--accent-soft);
    margin-bottom: 7pt;
}}
.sheet-contact {{
    text-align: center;
    font-size: var(--size-meta);
    color: var(--muted);
}}
.sheet-header-divider {{
    padding-bottom: 8pt;
    margin-bottom: 12pt;
    border-bottom: 0.75pt solid var(--line);
}}
.sheet-links {{
    text-align: center;
    font-size: var(--size-meta);
    color: var(--muted);
    margin-top: 3pt;
}}
.sheet-link-anchor, .sheet-links a {{
    color: var(--accent-soft);
    font-weight: 600;
    text-decoration: underline;
}}
.sheet-heading {{
    font-size: var(--size-heading);
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    border-bottom: 1.5pt solid var(--gold);
    padding-bottom: 5pt;
    margin: 16pt 0 6pt;
    page-break-after: avoid;
}}
.sheet-body {{ font-size: var(--size-body); margin-bottom: 4pt; white-space: pre-wrap; }}
.sheet-label-value {{ font-size: var(--size-body); margin-bottom: 4pt; }}
.sheet-lv-label {{ font-weight: 700; color: var(--accent-soft); }}
.sheet-block {{ page-break-inside: avoid; margin-bottom: 2pt; }}
.sheet-job-head {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-top: 12pt;
}}
.sheet-job-title-line {{ display: inline-flex; align-items: baseline; flex-wrap: wrap; }}
.sheet-job-title {{ font-size: var(--size-heading); font-weight: 700; color: var(--accent); }}
.sheet-job-type {{ font-size: var(--size-meta); font-style: italic; color: var(--muted); white-space: nowrap; }}
.sheet-job-dates {{ font-size: var(--size-meta); font-style: italic; color: var(--muted); white-space: nowrap; padding-left: 10pt; }}
.sheet-company {{ margin: 1pt 0 3pt; font-size: var(--size-body); font-weight: 700; font-style: italic; color: var(--accent-soft); }}
.sheet-company a, .sheet-project-link, .sheet-edu-school a {{
    color: var(--accent-soft);
    text-decoration: underline;
}}
.sheet-edu-school-plain {{ color: var(--muted); }}
.sheet-project-heading {{ font-size: var(--size-body); font-weight: 700; color: var(--text); margin: 8pt 0 2pt 0.10in; }}
.sheet-bullet-mark {{ color: var(--accent-soft); font-weight: 700; }}
.sheet-bullet {{ font-size: var(--size-body); margin: 0 0 3pt 0.20in; }}
.sheet-bullet-indent {{ margin-left: 0.32in; }}
.sheet-bullet-line {{ margin: 0 0 3pt 0; }}
.sheet-bullet-line:last-child {{ margin-bottom: 0; }}
.sheet-edu-line {{ font-size: var(--size-body); margin-top: 1pt; }}
.sheet-edu-degree {{ font-weight: 700; }}
.sheet-edu-sep {{ color: var(--muted); }}
.sheet-meta {{ font-size: var(--size-meta); font-style: italic; color: var(--muted); margin: 1pt 0 8pt; }}
.sheet-pub-title {{ font-weight: 700; }}
.sheet-pub-detail {{ margin-left: 0.20in; }}

/* ---------------------------------------------------- active-field highlight - */
/* .hl (green) marks the whole content zone a field belongs to; .hl-yellow
   marks the exact text of the input box currently focused, which may be a
   smaller piece nested inside that same green zone (e.g. just the "Phone"
   bit within the combined contact line). Both can apply to the same
   element when a field has no smaller piece to single out. */
.hl {{
    background: rgba(58, 150, 94, 0.20);
    box-shadow: 0 0 0 4px rgba(58, 150, 94, 0.20);
    border-radius: 4px;
    animation: hl-in 0.5s ease-out;
}}
@keyframes hl-in {{
    from {{ background: rgba(58, 150, 94, 0.50); box-shadow: 0 0 0 4px rgba(58, 150, 94, 0.50); }}
    to   {{ background: rgba(58, 150, 94, 0.20); box-shadow: 0 0 0 4px rgba(58, 150, 94, 0.20); }}
}}
.hl-yellow {{
    background: rgba(255, 196, 0, 0.60);
    border-radius: 3px;
    animation: hl-in-yellow 0.5s ease-out;
}}
@keyframes hl-in-yellow {{
    from {{ background: rgba(255, 196, 0, 0.90); }}
    to   {{ background: rgba(255, 196, 0, 0.60); }}
}}
"""


def describe_field(field_id):
    """Human-readable "what am I editing" label for the preview toolbar,
    in whichever language is currently active."""
    if not field_id:
        return None
    field_labels = {
        "personal.name": t("personal.full_name"),
        "personal.title": t("badge.professional_title"),
        "personal.contact": t("badge.contact_info"),
        "summary": t("nav.summary"),
    }
    if field_id in field_labels:
        return field_labels[field_id]
    section_labels = {
        "links": t("personal.links_title"),
        "skills": t("nav.skills"),
        "experience": t("nav.experience"),
        "education": t("nav.education"),
        "publications": t("nav.publications"),
        "certificates": t("nav.certificates"),
        "additional": t("nav.additional"),
    }
    return section_labels.get(field_id.split(".", 1)[0])


def _e(text):
    return html.escape(text or "", quote=True)


def _link_or_text(text, url, css_class=""):
    text = _e(text)
    url = (url or "").strip()
    if url:
        return f'<a class="{css_class}" href="{html.escape(url, quote=True)}">{text}</a>'
    return f'<span>{text}</span>'


def _field_tag(tag, css_class, field_id, active_field, active_field_precise, inner,
                precise_field_id=None, extra_attrs=""):
    """Render `<tag class="css_class [hl] [hl-yellow]" data-field=... extra_attrs>inner</tag>`.

    `field_id` drives the green "content zone" highlight (`.hl`) — the
    whole group a field belongs to. `precise_field_id` (defaults to
    `field_id` when there's nothing smaller to single out) drives the
    yellow "exact input box" highlight (`.hl-yellow`). Both can land on the
    same element at once."""
    precise_field_id = precise_field_id or field_id
    classes = css_class
    data_attr = ""
    if field_id:
        data_attr = f' data-field="{html.escape(field_id, quote=True)}"'
        if field_id == active_field:
            classes = f"{classes} hl"
    if precise_field_id:
        data_attr += f' data-field-precise="{html.escape(precise_field_id, quote=True)}"'
        if precise_field_id == active_field_precise:
            classes = f"{classes} hl-yellow"
    return f'<{tag} class="{classes}"{data_attr}{extra_attrs}>{inner}</{tag}>'


def render_resume_html(data: dict, active_field: str = None, active_field_precise: str = None) -> str:
    personal = data.get("personal", {})
    lang = data.get("language") or DEFAULT_LANGUAGE
    parts = []
    page_css = build_page_css(resolve_style(data))

    name = (personal.get("name") or "").strip()
    if not name and not data.get("summary") and not data.get("experience"):
        body = '<div class="sheet-empty">Start filling in Personal Info to see your resume take shape here.</div>'
        return f"<!doctype html><html><head><meta charset='utf-8'><style>{page_css}</style></head>" \
               f"<body><div class='sheet'>{body}</div></body></html>"

    def ftag(tag, css_class, field_id, inner, precise_field_id=None, extra_attrs=""):
        return _field_tag(tag, css_class, field_id, active_field, active_field_precise, inner,
                           precise_field_id=precise_field_id, extra_attrs=extra_attrs)

    def label_value_row(prefix, i, row):
        """Shared by Core Competencies / Certificates / Additional Info: a
        label span and a value span, each its own precise (yellow) target,
        inside one shared content-zone (green) container."""
        label_html = ""
        if row.get("label"):
            label_html = ftag("span", "sheet-lv-label", None, f"{_e(row['label'])}:  ",
                               precise_field_id=f"{prefix}.{i}.label")
        value_html = ftag("span", "", None, _e(row.get("value", "")),
                           precise_field_id=f"{prefix}.{i}.value")
        return ftag("div", "sheet-label-value", f"{prefix}.{i}", f"{label_html}{value_html}")

    parts.append(ftag("div", "sheet-name", "personal.name", _e(name.upper())))
    if personal.get("title"):
        parts.append(ftag("div", "sheet-title", "personal.title", _e(personal["title"])))

    contact_pairs = [(k, personal.get(k)) for k in resolve_contact_order(data) if personal.get(k)]
    link_rows = [r for r in data.get("links", []) if r.get("label") or r.get("value")]

    if contact_pairs:
        items = [
            ftag("span", "", None, _e(v), precise_field_id=f"personal.contact.{k}")
            for k, v in contact_pairs
        ]
        contact_html = "   &bull;   ".join(items)
        contact_class = "sheet-contact" if link_rows else "sheet-contact sheet-header-divider"
        parts.append(ftag("div", contact_class, "personal.contact", contact_html))

    if link_rows:
        items = [
            ftag("span", "sheet-link-item", f"links.{i}",
                 _link_or_text(row.get("label", ""), row.get("value", ""), "sheet-link-anchor"))
            for i, row in enumerate(link_rows)
        ]
        links_html = "   &bull;   ".join(items)
        parts.append(f'<div class="sheet-links sheet-header-divider">{links_html}</div>')

    def heading(text):
        parts.append(f'<div class="sheet-heading">{_e(text)}</div>')

    def render_summary():
        if not data.get("summary"):
            return
        heading(t("resume.summary", lang=lang))
        parts.append(ftag("div", "sheet-body", "summary", _e(data["summary"])))

    def render_skills():
        rows = [r for r in data.get("skills", []) if r.get("label") or r.get("value")]
        if not rows:
            return
        heading(t("resume.skills", lang=lang))
        for i, row in enumerate(rows):
            parts.append(label_value_row("skills", i, row))

    def job_dates_html(i, job):
        """The dates line — one green content-zone (the whole line), but
        start and end are each their own yellow "exact input box" target
        when both are present."""
        start = (job.get("start_date") or "").strip()
        end = (job.get("end_date") or "").strip()
        if start and end:
            inner = (
                ftag("span", "", None, _e(start), precise_field_id=f"experience.{i}.dates.start")
                + " &ndash; "
                + ftag("span", "", None, _e(end), precise_field_id=f"experience.{i}.dates.end")
            )
        elif start:
            inner = ftag("span", "", None, _e(start), precise_field_id=f"experience.{i}.dates.start")
        elif end:
            inner = ftag("span", "", None, _e(end), precise_field_id=f"experience.{i}.dates.end")
        else:
            inner = _e(job.get("dates", ""))  # older drafts stored one combined string
        return ftag("span", "sheet-job-dates", f"experience.{i}.dates", inner)

    def render_experience():
        jobs = [j for j in data.get("experience", []) if j.get("title") or j.get("company")]
        if not jobs:
            return
        heading(t("resume.experience", lang=lang))
        for i, job in enumerate(jobs):
            parts.append('<div class="sheet-block">')
            title_span = ftag("span", "sheet-job-title", f"experience.{i}.title", _e(job.get("title", "")))
            employment_display = format_employment_type((job.get("employment_type") or "").strip(), lang)
            title_line_inner = title_span
            if employment_display:
                title_line_inner += ftag(
                    "span", "sheet-job-type", f"experience.{i}.employment_type", f"&nbsp;&middot; {_e(employment_display)}",
                )
            title_line = f'<span class="sheet-job-title-line">{title_line_inner}</span>'
            dates_span = job_dates_html(i, job)
            parts.append(f'<div class="sheet-job-head">{title_line}{dates_span}</div>')
            if job.get("company"):
                company_inner = _link_or_text(job["company"], job.get("company_url"))
                parts.append(ftag("div", "sheet-company", f"experience.{i}.company", company_inner))
            for j, proj in enumerate(job.get("projects", [])):
                name_ = (proj.get("name") or "").strip()
                heading_field = f"experience.{i}.projects.{j}.heading"
                if name_:
                    heading_inner = (
                        '<span class="sheet-bullet-mark">&#8227;  </span>'
                        f'{_link_or_text(name_, proj.get("url"), "sheet-project-link")}'
                    )
                    parts.append(ftag("div", "sheet-project-heading", heading_field, heading_inner))
                bullet_class = "sheet-bullet sheet-bullet-indent" if name_ else "sheet-bullet"
                bullets_field = f"experience.{i}.projects.{j}.bullets"
                bullet_lines = [b for b in proj.get("bullets", []) if b.strip()]
                if bullet_lines:
                    bullets_html = "".join(
                        f'<div class="sheet-bullet-line"><span class="sheet-bullet-mark">&bull;  </span>'
                        f'<span>{_e(bullet.strip())}</span></div>'
                        for bullet in bullet_lines
                    )
                    parts.append(ftag("div", bullet_class, bullets_field, bullets_html))
            parts.append('</div>')

    def render_education():
        edu_rows = [e for e in data.get("education", []) if e.get("degree")]
        if not edu_rows:
            return
        heading(t("resume.education", lang=lang))
        for i, edu in enumerate(edu_rows):
            parts.append('<div class="sheet-block">')
            line = ftag("span", "sheet-edu-degree", None, _e(edu.get("degree", "")),
                        precise_field_id=f"education.{i}.degree")
            if edu.get("school"):
                line += '<span class="sheet-edu-sep">  &mdash;  </span>'
                if (edu.get("school_url") or "").strip():
                    school_inner = _link_or_text(edu["school"], edu.get("school_url"), "sheet-edu-school")
                else:
                    school_inner = f'<span class="sheet-edu-school-plain">{_e(edu["school"])}</span>'
                line += ftag("span", "", None, school_inner,
                             precise_field_id=f"education.{i}.school")
            parts.append(ftag("div", "sheet-edu-line", f"education.{i}.line", line))
            if edu.get("meta"):
                parts.append(ftag("div", "sheet-meta", f"education.{i}.meta", _e(edu["meta"])))
            parts.append('</div>')

    def render_publications():
        pubs = [p for p in data.get("publications", []) if p.get("title") or p.get("detail")]
        if not pubs:
            return
        heading(t("resume.publications", lang=lang))
        for i, item in enumerate(pubs):
            parts.append('<div class="sheet-block">')
            title_inner = (
                '<span class="sheet-bullet-mark">&bull;  </span>'
                f'<span class="sheet-pub-title">{_e(item.get("title", ""))}</span>'
            )
            parts.append(ftag("div", "sheet-bullet", f"publications.{i}.title", title_inner))
            if item.get("detail"):
                parts.append(ftag("div", "sheet-meta sheet-pub-detail", f"publications.{i}.detail",
                                   _e(item["detail"])))
            parts.append('</div>')

    def render_certificates():
        rows = [r for r in data.get("certificates", []) if r.get("label") or r.get("value")]
        if not rows:
            return
        heading(t("resume.certificates", lang=lang))
        for i, row in enumerate(rows):
            parts.append(label_value_row("certificates", i, row))

    def render_additional():
        rows = [r for r in data.get("additional", []) if r.get("label") or r.get("value")]
        if not rows:
            return
        heading(t("resume.additional", lang=lang))
        for i, row in enumerate(rows):
            parts.append(label_value_row("additional", i, row))

    section_renderers = {
        "summary": render_summary,
        "skills": render_skills,
        "experience": render_experience,
        "education": render_education,
        "publications": render_publications,
        "certificates": render_certificates,
        "additional": render_additional,
    }
    for key in resolve_section_order(data):
        section_renderers[key]()

    body = "".join(parts)
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{page_css}</style></head>"
        f"<body><div class='sheet'>{body}</div></body></html>"
    )


class PreviewPanel(QWidget):
    """Right-hand live preview: a small toolbar (title + zoom controls) above
    a QWebEngineView rendering the resume as an actual formatted page."""

    DEFAULT_ZOOM = 0.85
    style_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = self.DEFAULT_ZOOM

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        bar = QFrame()
        bar.setObjectName("PreviewBar")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(16, 10, 12, 10)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        title = QLabel(t("generate.live_preview"))
        title.setObjectName("PreviewTitle")
        hint = QLabel(t("preview.updates_automatically"))
        hint.setObjectName("PreviewHint")
        title_box.addWidget(title)
        title_box.addWidget(hint)
        bar_layout.addLayout(title_box)

        self.editing_badge = QLabel("")
        self.editing_badge.setObjectName("PreviewEditingBadge")
        self.editing_badge.hide()
        bar_layout.addSpacing(10)
        bar_layout.addWidget(self.editing_badge)

        bar_layout.addStretch(1)

        style_btn = QPushButton(t("common.style_settings"))
        style_btn.setProperty("variant", "ghostSmall")
        style_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        style_btn.setFixedHeight(26)
        style_btn.clicked.connect(self.style_requested.emit)
        bar_layout.addWidget(style_btn)
        bar_layout.addSpacing(8)

        zoom_out = QPushButton("−")
        zoom_in = QPushButton("+")
        for b in (zoom_out, zoom_in):
            b.setProperty("variant", "ghostSmall")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(26)
            b.setFixedWidth(30)
        zoom_out.clicked.connect(lambda: self._nudge_zoom(-0.08))
        zoom_in.clicked.connect(lambda: self._nudge_zoom(0.08))

        self.zoom_spin = QSpinBox()
        self.zoom_spin.setObjectName("ZoomPercentSpin")
        self.zoom_spin.setRange(40, 160)
        self.zoom_spin.setSingleStep(8)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.zoom_spin.setFixedSize(54, 26)
        self.zoom_spin.setCursor(Qt.CursorShape.IBeamCursor)
        self.zoom_spin.setToolTip("Type an exact zoom percentage")
        # editingFinished (Enter / focus-out) is a real edit; setValue() calls
        # made elsewhere to just *display* the current zoom don't trigger it,
        # so there's no risk of this looping back on itself.
        self.zoom_spin.editingFinished.connect(self._on_zoom_spin_edited)

        bar_layout.addWidget(zoom_out)
        bar_layout.addWidget(self.zoom_spin)
        bar_layout.addWidget(zoom_in)
        self._update_zoom_label()

        layout.addWidget(bar)

        host = QWidget()
        host.setObjectName("PreviewHost")
        host_layout = QVBoxLayout(host)
        host_layout.setContentsMargins(0, 0, 0, 0)
        self.view = QWebEngineView()
        self.view.setZoomFactor(self._zoom)
        self.view.setHtml(render_resume_html({}))
        self.view.loadFinished.connect(self._on_load_finished)
        # QtWebEngine handles Ctrl+wheel / Ctrl+= / Ctrl+- page zoom itself,
        # bypassing our own setZoomFactor() calls entirely — this is the
        # only way to find out it happened and keep the label honest.
        self.view.page().zoomFactorChanged.connect(self._on_zoom_factor_changed)
        host_layout.addWidget(self.view)
        layout.addWidget(host, 1)

        self._last_html = None
        self._active_field = None
        self._pending_scroll = None  # (active_field, field_changed, QPointF scroll_pos)

    def _nudge_zoom(self, delta):
        self._set_zoom(self._zoom + delta)

    def _set_zoom(self, zoom):
        self._zoom = max(0.4, min(1.6, round(zoom, 2)))
        self.view.setZoomFactor(self._zoom)
        self._update_zoom_label()

    def _update_zoom_label(self):
        self.zoom_spin.blockSignals(True)
        self.zoom_spin.setValue(round(self._zoom * 100))
        self.zoom_spin.blockSignals(False)

    def _on_zoom_spin_edited(self):
        self._set_zoom(self.zoom_spin.value() / 100)

    def _on_zoom_factor_changed(self, factor):
        # Fires for zooming done any way — our buttons, Ctrl+wheel, or
        # Ctrl+=/Ctrl+-. Don't clamp to the +/- buttons' 0.4–1.6 range here;
        # just reflect whatever QtWebEngine actually applied.
        self._zoom = round(factor, 2)
        self._update_zoom_label()

    def update_data(self, data: dict, active_field: str = None, active_field_precise: str = None,
                     force: bool = False):
        html_str = render_resume_html(data, active_field=active_field, active_field_precise=active_field_precise)
        field_changed = active_field != self._active_field
        if force or html_str != self._last_html or field_changed:
            # setHtml() is a fresh page load, which would otherwise reset the
            # scroll position to the top on every refresh — capture it here
            # so it can be restored once the reload completes.
            scroll_pos = self.view.page().scrollPosition()
            self._pending_scroll = (active_field, field_changed, scroll_pos)
            self._last_html = html_str
            self._active_field = active_field
            self.view.setHtml(html_str)

        label = describe_field(active_field)
        self.editing_badge.setText(f"●  Editing: {label}" if label else "")
        self.editing_badge.setVisible(bool(label))

    def _on_load_finished(self, ok):
        pending, self._pending_scroll = self._pending_scroll, None
        if not ok or pending is None:
            return
        active_field, field_changed, scroll_pos = pending
        if active_field and field_changed:
            # Just switched to editing a new field — bring it into view (but
            # only if it isn't already visible, so tabbing between fields
            # that are already on-screen doesn't cause needless scrolling).
            field_js = json.dumps(active_field)
            js = f"""
            (function() {{
                var el = document.querySelector('[data-field="' + {field_js} + '"]');
                if (!el) return;
                var r = el.getBoundingClientRect();
                if (r.top < 0 || r.bottom > window.innerHeight) {{
                    el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                }}
            }})();
            """
            self.view.page().runJavaScript(js)
        elif scroll_pos is not None and (scroll_pos.x() or scroll_pos.y()):
            self.view.page().runJavaScript(f"window.scrollTo({scroll_pos.x()}, {scroll_pos.y()});")
