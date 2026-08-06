"""
Resume Builder — PySide6 Edition
A polished, professional desktop tool for building a resume with a live
preview, exporting straight to Word (.docx) or PDF.

Run:
    pip install -r requirements.txt
    python main.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

import theme
from main_window import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Resume Builder")
    app.setOrganizationName("Resume Builder")

    theme.resolve_fonts()
    app.setFont(theme.base_font(10))
    app.setStyleSheet(theme.build_stylesheet())
    app.setWindowIcon(theme.make_app_icon())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
