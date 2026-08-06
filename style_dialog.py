"""
style_dialog.py
A non-modal "Resume Style" panel — font, sizes, colors, page background.
Every control applies instantly (to the live preview and, in turn, to what
gets exported), so there's no separate OK/Apply step to remember.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog, QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QVBoxLayout,
)

import theme
from i18n import t
from resume_style import DEFAULT_STYLE, FONT_CHOICES, SIZE_BOUNDS, STYLE_PRESETS
from widgets import button, hairline, micro_label


class ColorSwatch(QPushButton):
    """A small clickable color chip — opens a QColorDialog and reports the
    chosen color as an uppercase hex string."""

    colorChanged = Signal(str)

    def __init__(self, hex_color, tooltip="", parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip)
        self._hex = hex_color
        self.clicked.connect(self._pick_color)
        self._apply()

    def _apply(self):
        self.setStyleSheet(
            f"QPushButton {{ background: {self._hex}; border: 1.5px solid rgba(0,0,0,70); "
            f"border-radius: 5px; }}"
            f"QPushButton:hover {{ border: 1.5px solid rgba(0,0,0,140); }}"
        )

    def hex_color(self):
        return self._hex

    def set_hex_color(self, hex_color):
        if hex_color and hex_color != self._hex:
            self._hex = hex_color
            self._apply()

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self._hex), self, t("style.choose_color"))
        if color.isValid():
            self.set_hex_color(color.name().upper())
            self.colorChanged.emit(self._hex)


def _size_fields():
    return [
        ("size_name", t("style.size_name")),
        ("size_title", t("style.size_title")),
        ("size_heading", t("style.size_heading")),
        ("size_body", t("style.size_body")),
        ("size_meta", t("style.size_meta")),
    ]


def _color_fields():
    # Doubled "&&" — QFormLayout.addRow(str, widget) treats a lone "&" as a
    # mnemonic marker (it gets swallowed and the next letter underlined).
    return [
        ("accent_color", t("style.color_accent")),
        ("accent_soft_color", t("style.color_accent_soft")),
        ("highlight_color", t("style.color_highlight")),
        ("text_color", t("style.color_text")),
        ("muted_color", t("style.color_muted")),
        ("background_color", t("style.color_background")),
    ]


class StyleDialog(QDialog):
    """Resume-wide style controls. Non-modal — the live preview keeps
    updating behind it as you change fonts, sizes, and colors."""

    style_changed = Signal(dict)

    def __init__(self, style, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("style.title"))
        self.setModal(False)
        self.setMinimumWidth(380)
        self._updating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 20)
        layout.setSpacing(0)

        title = QLabel(t("style.title"))
        title.setFont(theme.serif_font(17, weight=700))
        layout.addWidget(title)
        hint = QLabel(t("style.hint"))
        hint.setProperty("role", "hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addSpacing(16)

        layout.addWidget(micro_label(t("style.presets")))
        layout.addSpacing(6)
        self.preset_combo = QComboBox()
        self.preset_combo.addItem(t("style.choose_preset"))
        self.preset_combo.addItems(list(STYLE_PRESETS.keys()))
        layout.addWidget(self.preset_combo)
        layout.addSpacing(18)
        layout.addWidget(hairline())
        layout.addSpacing(16)

        layout.addWidget(micro_label(t("style.font")))
        layout.addSpacing(6)
        self.font_combo = QComboBox()
        self.font_combo.addItems(FONT_CHOICES)
        layout.addWidget(self.font_combo)
        layout.addSpacing(16)

        layout.addWidget(micro_label(t("style.font_sizes")))
        layout.addSpacing(6)
        size_form = QFormLayout()
        size_form.setSpacing(8)
        size_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.size_spins = {}
        for key, label in _size_fields():
            lo, hi = SIZE_BOUNDS[key]
            spin = QSpinBox()
            spin.setRange(lo, hi)
            spin.setSuffix(" pt")
            spin.setCursor(Qt.CursorShape.PointingHandCursor)
            size_form.addRow(label, spin)
            self.size_spins[key] = spin
        layout.addLayout(size_form)

        layout.addSpacing(18)
        layout.addWidget(hairline())
        layout.addSpacing(16)

        layout.addWidget(micro_label(t("style.colors")))
        layout.addSpacing(6)
        color_form = QFormLayout()
        color_form.setSpacing(10)
        color_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.color_swatches = {}
        for key, label in _color_fields():
            swatch = ColorSwatch(DEFAULT_STYLE[key], tooltip=f"{label}")
            color_form.addRow(label, swatch)
            self.color_swatches[key] = swatch
        layout.addLayout(color_form)

        layout.addSpacing(10)
        bg_note = QLabel(t("style.bg_note"))
        bg_note.setProperty("role", "hint")
        bg_note.setWordWrap(True)
        layout.addWidget(bg_note)

        layout.addSpacing(16)
        layout.addWidget(hairline())
        layout.addSpacing(14)

        footer = QHBoxLayout()
        reset_btn = button(t("style.reset_default"), variant="secondary")
        reset_btn.clicked.connect(self._reset_to_default)
        close_btn = button(t("style.close"), variant="primary")
        close_btn.clicked.connect(self.close)
        footer.addWidget(reset_btn)
        footer.addStretch(1)
        footer.addWidget(close_btn)
        layout.addLayout(footer)

        # Wire live-update signals only after every control exists, then
        # populate from the incoming style (guarded, so this doesn't itself
        # fire a style_changed the moment the dialog opens).
        self.preset_combo.currentIndexChanged.connect(self._apply_preset)
        self.font_combo.currentTextChanged.connect(self._on_control_changed)
        for spin in self.size_spins.values():
            spin.valueChanged.connect(self._on_control_changed)
        for swatch in self.color_swatches.values():
            swatch.colorChanged.connect(self._on_control_changed)

        self.set_style(style)

    def set_style(self, style):
        """Populate every control from `style` without emitting style_changed."""
        self._updating = True
        idx = self.font_combo.findText(style.get("font_family", DEFAULT_STYLE["font_family"]))
        self.font_combo.setCurrentIndex(idx if idx >= 0 else 0)
        for key, spin in self.size_spins.items():
            spin.setValue(int(style.get(key, DEFAULT_STYLE[key])))
        for key, swatch in self.color_swatches.items():
            swatch.set_hex_color(style.get(key, DEFAULT_STYLE[key]))
        self.preset_combo.setCurrentIndex(0)
        self._updating = False

    def _current_style(self):
        style = {"font_family": self.font_combo.currentText()}
        style.update({key: spin.value() for key, spin in self.size_spins.items()})
        style.update({key: swatch.hex_color() for key, swatch in self.color_swatches.items()})
        return style

    def _on_control_changed(self, *_args):
        if self._updating:
            return
        self.style_changed.emit(self._current_style())

    def _apply_preset(self, index):
        if self._updating or index <= 0:
            return
        preset = STYLE_PRESETS.get(self.preset_combo.itemText(index))
        if not preset:
            return
        merged = dict(DEFAULT_STYLE)
        merged.update(preset)
        self.set_style(merged)
        self.style_changed.emit(merged)

    def _reset_to_default(self):
        self.set_style(DEFAULT_STYLE)
        self.style_changed.emit(dict(DEFAULT_STYLE))
