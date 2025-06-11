import sys

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from src.quilt.ui.windows import QuiltApplication

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