import sys

from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QIcon, QFont, QFontDatabase, QCursor
from PySide6.QtWidgets import *

from src.quilt.ui.widgets import QuiltApplication

def main():
    # Initialize the application
    app = QApplication(sys.argv)

    # Load the font
    font_id = QFontDatabase.addApplicationFont("assets/fonts/Roboto-Regular.ttf")
    
    if font_id == -1:
        print("Failed to load font! Loading default font instead.")
    else:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 10))

    quilt = QuiltApplication()
    quilt.show()
    sys.exit(app.exec())