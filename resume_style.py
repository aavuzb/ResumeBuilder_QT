"""
resume_style.py
The resume's own visual identity — font, sizes, colors, page background —
as distinct from theme.py (the *app's* navy/brass chrome). Shared, GUI-free
source of truth for defaults/bounds/sanitization so preview.py (live HTML)
and docx_engine.py (the actual exported file) never drift apart.
"""

import re

DEFAULT_STYLE = {
    "font_family": "Calibri",
    "accent_color": "#173A56",        # name, section headings
    "accent_soft_color": "#3E6382",   # company/school names, title line
    "highlight_color": "#C7A252",     # heading underline / rule accent
    "text_color": "#212428",          # body text
    "muted_color": "#5B636B",         # dates, meta lines
    "background_color": "#FFFFFF",    # page/paper background
    "size_name": 20,
    "size_title": 12,
    "size_heading": 11,
    "size_body": 10,
    "size_meta": 9,
}

COLOR_KEYS = [k for k in DEFAULT_STYLE if k.endswith("_color")]
SIZE_KEYS = [k for k in DEFAULT_STYLE if k.startswith("size_")]

SIZE_BOUNDS = {
    "size_name": (14, 32),
    "size_title": (9, 18),
    "size_heading": (9, 16),
    "size_body": (8, 13),
    "size_meta": (7, 12),
}

# A curated set of widely-installed fonts spanning sans/serif looks. Word
# and LibreOffice substitute silently if a font isn't installed locally, so
# this list favors fonts that ship with Windows/macOS/Office by default.
FONT_CHOICES = [
    "Calibri", "Arial", "Helvetica", "Verdana", "Tahoma",
    "Georgia", "Cambria", "Garamond", "Times New Roman",
]

_SERIF_STACKS = {
    "Georgia": 'Georgia, "Times New Roman", serif',
    "Cambria": 'Cambria, Georgia, serif',
    "Garamond": 'Garamond, "Times New Roman", serif',
    "Times New Roman": '"Times New Roman", Times, serif',
}


def css_font_stack(font_family):
    """CSS font-family value with sensible same-genre fallbacks."""
    if font_family in _SERIF_STACKS:
        return _SERIF_STACKS[font_family]
    if font_family == "Calibri":
        return 'Calibri, "Segoe UI", Arial, sans-serif'
    return f'"{font_family}", Arial, sans-serif'


# A handful of ready-made looks so someone who doesn't want to pick six
# colors by hand still gets something polished in one click.
STYLE_PRESETS = {
    "Navy & Brass": {
        "font_family": "Calibri",
        "accent_color": "#173A56", "accent_soft_color": "#3E6382", "highlight_color": "#C7A252",
        "text_color": "#212428", "muted_color": "#5B636B", "background_color": "#FFFFFF",
    },
    "Charcoal & Slate": {
        "font_family": "Arial",
        "accent_color": "#1F2937", "accent_soft_color": "#4B5563", "highlight_color": "#9CA3AF",
        "text_color": "#111827", "muted_color": "#6B7280", "background_color": "#FFFFFF",
    },
    "Forest & Sand": {
        "font_family": "Georgia",
        "accent_color": "#1F3D2B", "accent_soft_color": "#4B6B4F", "highlight_color": "#C9A66B",
        "text_color": "#242420", "muted_color": "#6B6558", "background_color": "#FFFFFF",
    },
    "Burgundy Classic": {
        "font_family": "Cambria",
        "accent_color": "#5C1A2B", "accent_soft_color": "#8C4A5A", "highlight_color": "#B08D57",
        "text_color": "#2A2320", "muted_color": "#75655F", "background_color": "#FFFFFF",
    },
    "Modern Teal": {
        "font_family": "Verdana",
        "accent_color": "#0F4C4C", "accent_soft_color": "#2E7D7D", "highlight_color": "#D9A441",
        "text_color": "#1C1F1F", "muted_color": "#5F6B6B", "background_color": "#FFFFFF",
    },
}

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def resolve_style(data: dict) -> dict:
    """DEFAULT_STYLE overridden field-by-field by data["style"], with every
    value sanitized — a corrupt or partial draft degrades gracefully to
    sane defaults per-field rather than crashing an export."""
    style = dict(DEFAULT_STYLE)
    custom = data.get("style") or {}
    if not isinstance(custom, dict):
        return style
    for key, value in custom.items():
        if key not in DEFAULT_STYLE:
            continue
        if key in COLOR_KEYS:
            if isinstance(value, str) and _HEX_RE.match(value):
                style[key] = value.upper()
        elif key in SIZE_KEYS:
            lo, hi = SIZE_BOUNDS[key]
            try:
                n = round(float(value))
            except (TypeError, ValueError):
                continue
            style[key] = max(lo, min(hi, n))
        elif key == "font_family":
            if isinstance(value, str) and value.strip():
                style[key] = value.strip()
    return style
