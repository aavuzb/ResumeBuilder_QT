"""
theme.py
Visual identity for Resume Builder (Qt edition) — a restrained editorial
navy + brass palette, font fallback detection, the global stylesheet, and a
programmatically-drawn app icon (no external image assets required).
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPainterPath, QPixmap


# ---------------------------------------------------------------- palette --
NAVY = "#173A56"            # deep navy — primary accent
NAVY_HOVER = "#0F2740"      # pressed / active state
NAVY_SOFT = "#3E6382"       # secondary accent (sub-headings, hints)
NAVY_TINT = "#EAF0F4"       # very light navy tint for subtle fills

SIDEBAR_TOP = "#173049"
SIDEBAR_BOTTOM = "#0D1E30"
SIDEBAR_ACTIVE = "#1F4A6B"
SIDEBAR_TEXT = "#A9BFD3"
SIDEBAR_TEXT_ACTIVE = "#FFFFFF"
SIDEBAR_BORDER = "#0A1826"

GOLD = "#C7A252"            # warm brass accent — used sparingly
GOLD_SOFT = "#F6EFDE"
GOLD_HOVER = "#B78F3D"

BG = "#F2F4F7"               # app background (behind cards)
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E3E7EB"
SUBCARD_BG = "#FAFBFC"
SUBCARD_BORDER = "#E7EAED"

TEXT_DARK = "#1B1F23"
TEXT_GRAY = "#5B6570"
TEXT_MUTED = "#8B949E"
DANGER = "#AD3E36"
DANGER_SOFT = "#F6E0DE"
DANGER_BORDER = "#E7B8B3"
SUCCESS = "#1F6F4A"
SUCCESS_SOFT = "#E1F1E8"

SANS_FONT_CANDIDATES = [
    "Inter", "Segoe UI", "Helvetica Neue", "Helvetica", "Arial",
    "Noto Sans", "Ubuntu", "DejaVu Sans", "Liberation Sans",
]
SERIF_FONT_CANDIDATES = [
    "Source Serif Pro", "Georgia", "Times New Roman", "Noto Serif",
    "Liberation Serif", "DejaVu Serif", "Times",
]

SANS_FONT = "Sans Serif"
SERIF_FONT = "Serif"


def _pick_font(candidates, fallback):
    available = {f.lower() for f in QFontDatabase.families()}
    for name in candidates:
        if name.lower() in available:
            return name
    return fallback


def resolve_fonts():
    """Detect the best available fonts on this machine. Call once at startup."""
    global SANS_FONT, SERIF_FONT
    SANS_FONT = _pick_font(SANS_FONT_CANDIDATES, "Sans Serif")
    SERIF_FONT = _pick_font(SERIF_FONT_CANDIDATES, "Serif")
    return SANS_FONT, SERIF_FONT


def _as_weight(weight):
    return weight if isinstance(weight, QFont.Weight) else QFont.Weight(weight)


def base_font(size=10, weight=QFont.Weight.Normal, italic=False):
    f = QFont(SANS_FONT, size)
    f.setWeight(_as_weight(weight))
    f.setItalic(italic)
    return f


def serif_font(size=20, weight=QFont.Weight.Bold, italic=False):
    f = QFont(SERIF_FONT, size)
    f.setWeight(_as_weight(weight))
    f.setItalic(italic)
    return f


def make_app_icon() -> QIcon:
    """Draw a small monogram icon (navy rounded square + brass 'R') so the
    app has a real window/taskbar icon without shipping an image asset."""
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        radius = size * 0.22
        path.addRoundedRect(0, 0, size, size, radius, radius)
        p.fillPath(path, QColor(NAVY))

        p.setPen(QColor(GOLD))
        f = QFont(SERIF_FONT if SERIF_FONT != "Serif" else "Georgia", int(size * 0.58))
        f.setBold(True)
        p.setFont(f)
        p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "R")
        p.end()
        icon.addPixmap(pm)
    return icon


def build_stylesheet() -> str:
    return f"""
/* ------------------------------------------------------------- globals -- */
QWidget {{
    font-family: "{SANS_FONT}";
    font-size: 13px;
    color: {TEXT_DARK};
}}
QWidget#RootBg, QWidget#FormArea, QScrollArea#FormScroll {{
    background: {BG};
}}
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
QToolTip {{
    background: {NAVY};
    color: white;
    border: 1px solid {NAVY_HOVER};
    padding: 6px 10px;
    border-radius: 6px;
}}

/* -------------------------------------------------------------- sidebar - */
QFrame#Sidebar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {SIDEBAR_TOP}, stop:1 {SIDEBAR_BOTTOM});
    border-right: 1px solid {SIDEBAR_BORDER};
}}
QLabel#BrandBadge {{
    background: {GOLD};
    color: {NAVY};
    border-radius: 9px;
    font-weight: 700;
}}
QLabel#BrandTitle {{
    color: white;
    font-weight: 700;
}}
QLabel#BrandTag {{
    color: {SIDEBAR_TEXT};
}}
QFrame#SidebarHairline {{
    background: rgba(255, 255, 255, 28);
    max-height: 1px;
    min-height: 1px;
    border: none;
}}
QPushButton#NavButton {{
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 10px 18px;
    color: {SIDEBAR_TEXT};
}}
QPushButton#NavButton:hover {{
    background: rgba(255, 255, 255, 18);
}}
QPushButton#NavButton:checked {{
    background: {SIDEBAR_ACTIVE};
    border-left: 3px solid {GOLD};
}}
QPushButton#NavButton[dropIndicator="before"] {{
    border-top: 3px solid {GOLD};
}}
QPushButton#NavButton[dropIndicator="after"] {{
    border-bottom: 3px solid {GOLD};
}}
QLabel#NavStep {{
    color: {SIDEBAR_TEXT};
    font-weight: 600;
}}
QLabel#NavStep[active="true"] {{
    color: {GOLD};
}}
QLabel#NavText {{
    color: {SIDEBAR_TEXT};
}}
QLabel#NavText[active="true"] {{
    color: {SIDEBAR_TEXT_ACTIVE};
    font-weight: 600;
}}
QLabel#NavDot {{
    color: rgba(255, 255, 255, 40);
    font-size: 15px;
}}
QLabel#NavDot[filled="true"] {{
    color: {GOLD};
}}
QLabel#NavDragHandle {{
    color: rgba(255, 255, 255, 60);
    font-size: 12px;
}}
QLabel#NavDragHandle:hover {{
    color: {GOLD};
}}
QToolButton#NavReorderBtn {{
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 85);
    font-size: 7px;
    padding: 0;
}}
QToolButton#NavReorderBtn:hover:enabled {{
    color: {GOLD};
}}
QToolButton#NavReorderBtn:disabled {{
    color: rgba(255, 255, 255, 20);
}}
QPushButton#SidebarResetOrderButton {{
    background: transparent;
    border: none;
    color: {GOLD_HOVER};
    font-size: 10px;
    font-weight: 600;
    text-align: left;
    padding: 2px 0;
}}
QPushButton#SidebarResetOrderButton:hover {{
    color: {GOLD};
    text-decoration: underline;
}}
QPushButton#SidebarGhostButton {{
    background: rgba(255, 255, 255, 12);
    color: {SIDEBAR_TEXT};
    border: 1px solid rgba(255, 255, 255, 40);
    border-radius: 7px;
    padding: 7px 10px;
    font-size: 11px;
}}
QPushButton#SidebarGhostButton:hover {{
    background: rgba(255, 255, 255, 24);
    color: white;
}}
QComboBox#SidebarLanguageCombo {{
    background: rgba(255, 255, 255, 12);
    color: {SIDEBAR_TEXT_ACTIVE};
    border: 1px solid rgba(255, 255, 255, 40);
    border-radius: 7px;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 600;
}}
QComboBox#SidebarLanguageCombo:hover {{
    background: rgba(255, 255, 255, 24);
}}
QComboBox#SidebarLanguageCombo::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox#SidebarLanguageCombo QAbstractItemView {{
    background: {SIDEBAR_TOP};
    color: {SIDEBAR_TEXT_ACTIVE};
    border: 1px solid rgba(255, 255, 255, 40);
    selection-background-color: {SIDEBAR_ACTIVE};
    selection-color: white;
    outline: none;
}}
QLabel#SidebarFooterNote {{
    color: rgba(255, 255, 255, 70);
    font-size: 10px;
}}

/* ---------------------------------------------------------- page header - */
QLabel[role="eyebrow"] {{
    color: {GOLD_HOVER};
    font-weight: 700;
    font-size: 11px;
}}
QLabel[role="sectionTitle"] {{
    color: {TEXT_DARK};
    font-family: "{SERIF_FONT}";
}}
QLabel[role="hint"] {{
    color: {TEXT_GRAY};
    font-size: 12px;
}}
QLabel[role="microLabel"] {{
    color: {TEXT_MUTED};
    font-weight: 700;
    font-size: 10px;
}}
QFrame[role="hairline"] {{
    background: {CARD_BORDER};
    max-height: 1px;
    min-height: 1px;
    border: none;
}}

/* ------------------------------------------------------------ text input - */
QLineEdit, QPlainTextEdit, QTextEdit {{
    background: white;
    border: 1.4px solid {CARD_BORDER};
    border-radius: 8px;
    padding: 7px 10px;
    selection-background-color: {NAVY_TINT};
    selection-color: {TEXT_DARK};
}}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1.4px solid {NAVY};
}}
QLineEdit:disabled {{
    background: {SUBCARD_BG};
    color: {TEXT_MUTED};
}}
QLineEdit[bordered="subtle"] {{
    background: {SUBCARD_BG};
    border: 1.2px solid {SUBCARD_BORDER};
}}

/* --------------------------------------------------------------- combo box - */
QComboBox {{
    background: white;
    border: 1.4px solid {CARD_BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    color: {TEXT_DARK};
}}
QComboBox:focus {{
    border: 1.4px solid {NAVY};
}}
QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox QAbstractItemView {{
    background: white;
    border: 1px solid {CARD_BORDER};
    selection-background-color: {NAVY_TINT};
    selection-color: {TEXT_DARK};
    outline: none;
}}

/* ----------------------------------------------------------------- cards - */
QFrame#Card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-top: 3px solid {NAVY};
    border-radius: 12px;
}}
QFrame#SubCard {{
    background: {SUBCARD_BG};
    border: 1px solid {SUBCARD_BORDER};
    border-top: 3px solid {GOLD};
    border-radius: 10px;
}}
QFrame#SubCard[dropIndicator="before"] {{
    border-top: 2.5px solid {GOLD_HOVER};
}}
QFrame#SubCard[dropIndicator="after"] {{
    border-bottom: 2.5px solid {GOLD_HOVER};
}}
QFrame#Row {{
    background: {SUBCARD_BG};
    border: 1px solid {SUBCARD_BORDER};
    border-radius: 9px;
}}
QFrame#Row[dropIndicator="before"] {{
    border-top: 2.5px solid {GOLD_HOVER};
}}
QFrame#Row[dropIndicator="after"] {{
    border-bottom: 2.5px solid {GOLD_HOVER};
}}
QLabel#RowDragHandle {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}
QLabel#RowDragHandle:hover {{
    color: {GOLD_HOVER};
}}
QToolButton#RowReorderBtn {{
    background: transparent;
    border: none;
    color: {TEXT_MUTED};
    font-size: 7px;
    padding: 0;
}}
QToolButton#RowReorderBtn:hover:enabled {{
    color: {GOLD_HOVER};
}}
QToolButton#RowReorderBtn:disabled {{
    color: {CARD_BORDER};
}}
QLabel#CardBadge {{
    background: {NAVY};
    color: white;
    font-weight: 700;
    border-radius: 13px;
    font-size: 11px;
}}
QLabel#SubCardBadge {{
    background: {GOLD};
    color: {NAVY};
    font-weight: 700;
    border-radius: 10px;
    font-size: 10px;
}}

/* -------------------------------------------------------------- buttons - */
QPushButton {{
    font-family: "{SANS_FONT}";
}}
QPushButton[variant="primary"] {{
    background: {NAVY};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
}}
QPushButton[variant="primary"]:hover {{
    background: {NAVY_HOVER};
}}
QPushButton[variant="primary"]:pressed {{
    background: #0A1D30;
}}
QPushButton[variant="primary"]:disabled {{
    background: #9FB0BE;
}}
QPushButton[variant="gold"] {{
    background: {GOLD};
    color: {NAVY};
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
}}
QPushButton[variant="gold"]:hover {{
    background: {GOLD_HOVER};
    color: white;
}}
QPushButton[variant="gold"]:disabled {{
    background: #E3D5AF;
    color: white;
}}
QPushButton[variant="secondary"] {{
    background: white;
    color: {NAVY};
    border: 1.3px solid {CARD_BORDER};
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
}}
QPushButton[variant="secondary"]:hover {{
    background: {NAVY_TINT};
    border-color: {NAVY_SOFT};
}}
QPushButton[variant="ghost"] {{
    background: white;
    color: {NAVY};
    border: 1.3px solid {NAVY};
    border-radius: 7px;
    padding: 8px 16px;
    font-weight: 700;
    font-size: 12px;
}}
QPushButton[variant="ghost"]:hover {{
    background: {NAVY_TINT};
}}
QPushButton[variant="ghostSmall"] {{
    background: {SUBCARD_BG};
    color: {NAVY_SOFT};
    border: 1.2px solid {SUBCARD_BORDER};
    border-radius: 6px;
    padding: 5px 12px;
    font-weight: 700;
    font-size: 11px;
}}
QPushButton[variant="ghostSmall"]:hover {{
    background: {NAVY_TINT};
    border-color: {NAVY_SOFT};
}}
QSpinBox#ZoomPercentSpin {{
    background: {SUBCARD_BG};
    color: {TEXT_DARK};
    border: 1.2px solid {SUBCARD_BORDER};
    border-radius: 6px;
    padding: 5px 2px;
    font-size: 12px;
    font-weight: 600;
}}
QSpinBox#ZoomPercentSpin:focus {{
    border-color: {NAVY_SOFT};
    background: white;
}}
QPushButton[variant="danger"] {{
    background: white;
    color: {DANGER};
    border: 1.2px solid {DANGER_BORDER};
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}}
QPushButton[variant="danger"]:hover {{
    background: {DANGER_SOFT};
}}
QPushButton[variant="iconGhost"] {{
    background: transparent;
    color: {TEXT_MUTED};
    border: none;
    border-radius: 6px;
    font-weight: 700;
}}
QPushButton[variant="iconGhost"]:hover {{
    background: {DANGER_SOFT};
    color: {DANGER};
}}

/* ------------------------------------------------------------ status bar - */
QStatusBar {{
    background: {CARD_BG};
    border-top: 1px solid {CARD_BORDER};
    color: {TEXT_GRAY};
    padding: 2px 6px;
}}
QStatusBar[state="ok"] {{
    color: {SUCCESS};
}}
QStatusBar[state="err"] {{
    color: {DANGER};
}}
QLabel#StatusIcon {{
    font-weight: 700;
}}

/* ------------------------------------------------------------ splitter --- */
QSplitter::handle {{
    background: {CARD_BORDER};
    width: 1px;
}}

/* ---------------------------------------------------------- preview bar - */
QFrame#PreviewBar {{
    background: {CARD_BG};
    border-bottom: 1px solid {CARD_BORDER};
}}
QLabel#PreviewTitle {{
    color: {TEXT_DARK};
    font-weight: 700;
}}
QLabel#PreviewHint {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}
QLabel#PreviewEditingBadge {{
    color: {SUCCESS};
    background: {SUCCESS_SOFT};
    border-radius: 9px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}
QWidget#PreviewHost {{
    background: #DDE2E7;
}}

/* ---------------------------------------------------------- scrollbars -- */
QScrollBar:vertical {{
    background: transparent;
    width: 11px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: rgba(23, 58, 86, 60);
    min-height: 30px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(23, 58, 86, 110);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 11px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: rgba(23, 58, 86, 60);
    min-width: 30px;
    border-radius: 4px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* -------------------------------------------------------------- dialogs - */
QMessageBox {{
    background: {CARD_BG};
}}
QFileDialog {{
    background: {CARD_BG};
}}
"""
