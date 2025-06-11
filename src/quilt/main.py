import sys

from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QIcon, QFont, QFontDatabase, QCursor
from PySide6.QtWidgets import *

from src.quilt.ui.utils import load_icon, load_colored_icon, load_and_save_padded_icon
from src.quilt.ui.widgets import (
    QuiltTitleBar, QuiltFileSystemModel,
    QuiltPDFViewer, QuiltTreeView, QuiltErrorPopup,
    QuiltNotImplementedPopup, QuiltNavigationPane,
    QuiltMainView
)
from src.quilt.workspace import QuiltWorkspace

def load_stylesheet(style_name):
    with open(f'styles/{style_name}.qss', 'r') as file:
        return file.read()

class QuiltMainWindow(QMainWindow):
    toggle_layout_options = Signal(bool)
   
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quilt Application")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Tracking
        self._start_pos = None
        self._resizing = False
        self._resize_margin = 5
        self._resize_edge = None
        self.setMouseTracking(True)

        # Set window icon
        self.setWindowIcon(QIcon("assets/quilt-nomid.ico"))

        # Set window title
        self.setWindowTitle("Quilt")

        # Load stylesheets
        self.quilt_style = load_stylesheet("quilt-style")
        self.setStyleSheet(self.quilt_style)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        layout.addWidget(QuiltTitleBar(self))

        # Obtain starter layout
        layout.addWidget(self._build_start_layout())

        # Central widget
        central = QWidget()
        central.setLayout(layout)
        central.setStyleSheet(self.quilt_style)
        self.setCentralWidget(central)
        self._enable_tracking()


    def _build_start_layout(self):
        # Buttons
        btn_new = QToolButton(self)
        btn_open = QToolButton(self)
        btn_settings = QToolButton(self)

        # Set button properties
        btn_new.setObjectName("startup-button")
        btn_open.setObjectName("startup-button")
        btn_settings.setObjectName("startup-button")

        # Set icons for buttons
        btn_new.setIcon(load_icon("plus"))
        btn_open.setIcon(load_icon("folder-open"))
        btn_settings.setIcon(load_icon("gear"))

        # Connect buttons to their respective functions
        btn_new.clicked.connect(self._create_workspace)
        btn_open.clicked.connect(self._open_workspace)
        btn_settings.clicked.connect(self._open_settings)

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
        container = QWidget(self)
        v_layout = QVBoxLayout(self.centralWidget())
        v_layout.addStretch(1) # Top spacer
        v_layout.addLayout(h_layout)
        v_layout.addStretch(1) # Bottom spacer
        container.setLayout(v_layout)

        # Return the container layout
        return container

    def _build_feature_pane(self):
        pass

    def _create_workspace(self):
        QuiltNotImplementedPopup(self)

    def _open_workspace(self):
        # Open a file dialog to select a workspace
        workspace_dir = QFileDialog.getExistingDirectory(self, " Open Workspace")
        if workspace_dir:
            self.workspace = QuiltWorkspace(workspace_dir)

            # Obtain titlebar and layout
            titlebar = QuiltTitleBar(self)
            view = QuiltMainView(self, self.workspace, self.quilt_style)

            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(titlebar)
            layout.addWidget(view)

            # Central widget
            central = QWidget()
            central.setLayout(layout)
            central.setStyleSheet(self.quilt_style)
            self.setCentralWidget(central)
            self._enable_tracking()

            # Toggle layout options
            self.toggle_layout_options.connect(titlebar.toggle_layout_options)
            self.toggle_layout_options.emit(True)

            titlebar.toggle_navigation.connect(view.navigation_pane.toggle)
            titlebar.toggle_features.connect(view.feature_pane.toggle)

    def _open_settings(self):
        QuiltNotImplementedPopup(self)

    def _enable_tracking(self):
        self.setMouseTracking(True)
        self.centralWidget().setMouseTracking(True)
        for widget in self.findChildren(QWidget):
            widget.setMouseTracking(True)

    def _get_edge_at(self, pos):
        rect = self.rect()
        x, y = pos.x(), pos.y()
        margin = self._resize_margin

        left = x < margin
        right = x > rect.width() - margin
        top = y < margin
        bottom = y > rect.height() - margin

        if top and left:
            return 'top_left'
        elif top and right:
            return 'top_right'
        elif bottom and left:
            return 'bottom_left'
        elif bottom and right:
            return 'bottom_right'
        elif top:
            return 'top'
        elif bottom:
            return 'bottom'
        elif left:
            return 'left'
        elif right:
            return 'right'
        return None

    def _resize_window(self, global_pos):
        diff = global_pos - self._start_pos
        geom = self.geometry()

        if 'left' in self._resize_edge:
            new_x = geom.x() + diff.x()
            new_w = geom.width() - diff.x()
            if new_w > self.minimumWidth():
                geom.setX(new_x)
                geom.setWidth(new_w)

        if 'right' in self._resize_edge:
            new_w = geom.width() + diff.x()
            if new_w > self.minimumWidth():
                geom.setWidth(new_w)

        if 'top' in self._resize_edge:
            new_y = geom.y() + diff.y()
            new_h = geom.height() - diff.y()
            if new_h > self.minimumHeight():
                geom.setY(new_y)
                geom.setHeight(new_h)

        if 'bottom' in self._resize_edge:
            new_h = geom.height() + diff.y()
            if new_h > self.minimumHeight():
                geom.setHeight(new_h)

        self.setGeometry(geom)
        self._start_pos = global_pos

    def _update_cursor(self, edge):
        cursors = {
            'top_left': Qt.SizeFDiagCursor,
            'bottom_right': Qt.SizeFDiagCursor,
            'top_right': Qt.SizeBDiagCursor,
            'bottom_left': Qt.SizeBDiagCursor,
            'top': Qt.SizeVerCursor,
            'bottom': Qt.SizeVerCursor,
            'left': Qt.SizeHorCursor,
            'right': Qt.SizeHorCursor,
        }
        cursor = cursors.get(edge, Qt.ArrowCursor)
        self.setCursor(cursor)

    @Slot(bool)
    def _toggle_features_pane(self, visible):
        if visible:
            self.feature_pane.show()
            self.feature_pane.setMinimumSize(350, 0)
            self.main_splitter.setSizes([1, 1, 100])
        else:
            self.feature_pane.hide()
            self.main_splitter.setSizes([1, 1, 0])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_pos = event.globalPos()
            self._resize_edge = self._get_edge_at(event.pos())
            self._resizing = self._resize_edge is not None
            if self._resizing:
                event.accept()
            else:
                super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resize_edge = None
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._resize_edge:
            self._resize_window(event.globalPos())
            event.accept()
        else:
            edge = self._get_edge_at(event.pos())
            self._update_cursor(edge)
            super().mouseMoveEvent(event)

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

    quilt = QuiltMainWindow()
    quilt.show()
    sys.exit(app.exec())