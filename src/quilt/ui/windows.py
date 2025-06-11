from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog

from src.quilt.ui.widgets import QuiltTitleBar, QuiltStartView, QuiltMainView, QuiltNotImplementedPopup
from src.quilt.workspace import QuiltWorkspace

from src.quilt.ui.utils import load_stylesheet

class QuiltApplication(QMainWindow):
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

        # Obtain start view
        view = QuiltStartView(self)
        view.signal_new_workspace.connect(self._create_workspace)
        view.signal_open_workspace.connect(self._open_workspace)
        view.signal_open_settings.connect(self._open_settings)

        layout.addWidget(view)

        # Central widget
        central = QWidget()
        central.setLayout(layout)
        central.setStyleSheet(self.quilt_style)
        self.setCentralWidget(central)
        self._enable_tracking()

    @Slot()
    def _create_workspace(self):
        QuiltNotImplementedPopup(self)

    @Slot()
    def _open_workspace(self):
        # Open a file dialog to select a workspace
        workspace_dir = QFileDialog.getExistingDirectory(self, " Open Workspace")
        if workspace_dir:
            workspace = QuiltWorkspace(workspace_dir)

            # Obtain titlebar and layout
            titlebar = QuiltTitleBar(self)
            view = QuiltMainView(self, workspace, self.quilt_style)

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

    @Slot()
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