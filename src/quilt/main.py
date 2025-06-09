import sys

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QToolButton, QHBoxLayout, QVBoxLayout


def load_stylesheet(style_name):
    with open(f'styles/{style_name}.qss', 'r') as file:
        return file.read()


class QuiltStartupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quilt Application")
        self.setGeometry(100, 100, 800, 600)

        # Set window icon
        self.setWindowIcon(QIcon("assets/quilt.ico"))

        # Set window title
        self.setWindowTitle("Quilt")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Buttons
        btn_style = load_stylesheet("big-button-style")
        btn_new = QToolButton(self)
        btn_open = QToolButton(self)
        btn_settings = QToolButton(self)

        # Set icons for buttons
        btn_new.setIcon(QIcon("assets/plus-dark.png"))
        btn_open.setIcon(QIcon("assets/folder-open-dark.png"))
        btn_settings.setIcon(QIcon("assets/gear-dark.png"))

        # Set button sizes
        btn_new.setIconSize(QSize(28, 28))
        btn_open.setIconSize(QSize(28, 28))
        btn_settings.setIconSize(QSize(28, 28))

        btn_new.setFixedSize(QSize(64, 64))
        btn_open.setFixedSize(QSize(64, 64))
        btn_settings.setFixedSize(QSize(64, 64))

        # Set button tooltips
        btn_new.setToolTip("Create a new project")
        btn_open.setToolTip("Open an existing project")
        btn_settings.setToolTip("Open settings")

        # Apply styles to buttons
        btn_new.setStyleSheet(btn_style)
        btn_open.setStyleSheet(btn_style)
        btn_settings.setStyleSheet(btn_style)

        # Horizontal layout for buttons
        h_layout = QHBoxLayout()
        h_layout.addStretch(1) # Left spacer
        h_layout.addWidget(btn_new)
        h_layout.addSpacing(20)
        h_layout.addWidget(btn_open)
        h_layout.addSpacing(20)
        h_layout.addWidget(btn_settings)    
        h_layout.addStretch(1) # Right spacer

        # Vertical layout to center horizontal layout
        v_layout = QVBoxLayout(central_widget)
        v_layout.addStretch(1) # Top spacer
        v_layout.addLayout(h_layout)
        v_layout.addStretch(1) # Bottom spacer

        # Set the layout to the central widget
        central_widget.setLayout(v_layout)


def run_quilt():
    app = QApplication(sys.argv)
    start_window = QuiltStartupWindow()
    start_window.show()
    sys.exit(app.exec())