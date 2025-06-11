from typing import Optional

from PySide6.QtCore import Qt, QSize, QPoint, QUrl, Signal, Slot
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QDialog, 
    QFileDialog, QFileSystemModel,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy, QSplitter, QSplitterHandle, QStyle, QStyleOptionViewItem,  QStyledItemDelegate,
    QToolBar, QToolButton, QTreeView,
    QVBoxLayout,
    QWidget, QWidgetAction
)

from src.quilt.ui.utils import (
    load_and_save_padded_icon,
    load_colored_icon, 
    load_favicon, 
    load_icon,
    load_stylesheet
)
from src.quilt.workspace import QuiltWorkspace

class HoverAwareSplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)  
        self.setAttribute(Qt.WA_Hover, True)  # Force Qt to trigger hover events

class HoverAwareSplitter(QSplitter):
    def createHandle(self):
        return HoverAwareSplitterHandle(self.orientation(), self)

class QuiltErrorPopup(QDialog):
    def __init__(self, parent: Optional[QWidget] = None, title: str = '', message: str = ''):
        super().__init__(parent)
        self.setWindowTitle(title or "Error")
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setObjectName("error-popup")

        # Container
        container = QWidget()
        container.setObjectName("error-popup")

        # Icon and message
        icon = QIcon(load_colored_icon("warning-circle", "dark-red", 128, 128))
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(32, 32))
        icon_label.setAlignment(Qt.AlignCenter)

        text_label = QLabel(message)
        text_label.setWordWrap(False)
        text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # Layout
        message_layout = QHBoxLayout()
        message_layout.addWidget(icon_label)
        message_layout.addWidget(text_label)
        message_layout.setContentsMargins(10, 10, 10, 10)
        message_layout.setSpacing(10)

        # Ok button
        ok_button = QPushButton("OK")
        ok_button.setObjectName("error-popup-button")
        ok_button.clicked.connect(self.accept)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addLayout(message_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(button_layout)

        # Top level layout
        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(container)

        self.setLayout(container_layout)
        self.exec()


class QuiltNotImplementedPopup(QuiltErrorPopup):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent, title="Not Implemented", message="This feature is not yet implemented.")

class QuiltTitleBar(QWidget):
    """Custom title bar widget for Quilt windows."""
    toggle_navigation = Signal(bool)
    toggle_features = Signal(bool)

    navigation_toggled = True
    features_toggled = True

    def __init__(self, parent: Optional[QWidget] = None, title: str = " Quilt"):
        super().__init__(parent)
        self.parent = parent
        self.title = title

        self.setObjectName("title-bar")
        self.setFixedHeight(32)

        self._start_pos: Optional[QPoint] = None
        self._is_dragging = False
        self.layout_options = []

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left side
        favicon = load_favicon()
        favicon.setObjectName("favicon")

        title_label = QLabel(self.title)

        # Right side
        self.btn_show_navigation = self._create_button("sidebar-left", "Toggle Navigation Bar", self._toggle_navigation)
        self.btn_show_navigation.setObjectName("title-bar-small-button")
        self.btn_show_navigation.hide()

        self.btn_show_features = self._create_button("sidebar-right", "Toggle Secondary Bar", self._toggle_features)
        self.btn_show_features.setObjectName("title-bar-small-button")
        self.btn_show_features.hide()

        self.layout_options.append(self.btn_show_navigation)
        self.layout_options.append(self.btn_show_features)

        # Frame utility buttons
        self.btn_minimize = self._create_button("minus", "Minimize", self.parent.showMinimized)
        self.btn_restore = self._create_button("", "", self._toggle_state)
        self._update_restore_icon()

        self.btn_close = self._create_button("x", "Close", self.parent.close)
        self.btn_close.setObjectName("title-bar-close-button")

        layout.addWidget(favicon)
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(self.btn_show_navigation)
        layout.addWidget(self.btn_show_features)
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_restore)
        layout.addWidget(self.btn_close)

    def _create_button(self, icon_name: str, tooltip: str, callback) -> QPushButton:
        icon = QIcon(load_icon(icon_name)) if icon_name else QIcon()
        button = QPushButton(icon, "")
        button.setObjectName("title-bar-button")
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        return button

    def _toggle_navigation(self) -> None:
        self.navigation_toggled = not self.navigation_toggled
        self.toggle_navigation.emit(self.navigation_toggled)

    def _toggle_features(self) -> None:
        self.features_toggled = not self.features_toggled
        self.toggle_features.emit(self.features_toggled)

    def _update_restore_icon(self) -> None:
        if self.parent.isMaximized():
            icon, tooltip = "copy-simple", "Restore"
        else:
            icon, tooltip = "square", "Maximize"

        self.btn_restore.setIcon(QIcon(load_icon(icon)))
        self.btn_restore.setToolTip(tooltip)

    def _toggle_state(self) -> None:
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
        self._update_restore_icon()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._start_pos = event.globalPosition().toPoint()
            self._is_dragging = True
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._is_dragging and self._start_pos:
            offset = event.globalPosition().toPoint() - self._start_pos
            self._start_pos = event.globalPosition().toPoint()
            self.window().move(self.window().pos() + offset)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            event.accept()

    @Slot(bool)
    def toggle_layout_options(self, show_options) -> None:
        if show_options:
            [option.show() for option in self.layout_options]
        else:
            [option.hide() for option in self.layout_options]


class QuiltTreeItemDelegate(QStyledItemDelegate):
    """Custom delegate for styling items in the file tree view."""

    def paint(self, painter, option, index):
        style = option.widget.style()
        option_copy = QStyleOptionViewItem(option)

        if option.state & QStyle.State_Selected:
            style.drawPrimitive(QStyle.PE_PanelItemViewItem, option, painter, option.widget)

        if option.state & (QStyle.State_Selected | QStyle.State_MouseOver):
            option_copy.font.setBold(True)

        option_copy.state &= ~QStyle.State_Selected
        super().paint(painter, option_copy, index)


class QuiltTreeView(QTreeView):
    """Custom tree view for displaying file system with custom delegate and model."""
    pdf_selected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None, model: Optional[QFileSystemModel] = None,
                 workspace: Optional[QuiltWorkspace] = None, applied_style_sheet: str = ""):
        super().__init__(parent)
        self.workspace = workspace
        self.setObjectName("navigation-tree")
        self.setModel(model)
        self.setRootIndex(model.index(workspace.workspace_dir))
        self.setHeaderHidden(True)
        self.setFocusPolicy(Qt.NoFocus)  # Disable focus outline
        self.hideColumn(1)  # Size
        self.hideColumn(2)  # Type
        self.hideColumn(3)  # Last Modified
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setItemDelegate(QuiltTreeItemDelegate())  # Use custom delegate to prevent icon tinting
        self.setStyleSheet(applied_style_sheet)  # Apply the full stylesheet

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.position().toPoint())
            if index.isValid():
                self.setCurrentIndex(index)
                
                # Find file and metadata
                workspace_entry = self.workspace.find_pdf_from_name(index.data())
                if workspace_entry:
                    raw_path = workspace_entry['path']
                    pdf_path = str(raw_path).strip()  # Ensure it's a clean string
                    self.pdf_selected.emit(pdf_path)
        super().mousePressEvent(event)


class QuiltFileSystemModel(QFileSystemModel):
    """Custom file system model with icons based on file type."""

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DecorationRole and index.column() == 0:
            file_path = self.filePath(index)
            if file_path.endswith(".pdf"):
                return QIcon(load_icon("file-pdf"))
            elif file_path.endswith(".md"):
                return QIcon(load_icon("file-markdown"))
            elif file_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                return QIcon(load_icon("file-image"))
            elif self.isDir(index):
                return QIcon(load_icon("folder"))
        return super().data(index, role)


class QuiltPDFViewer(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("pdf-viewer")
    
        self.pdf_layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PluginsEnabled, True)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PdfViewerEnabled, True)
        self.pdf_layout.addWidget(self.web_view)

    @Slot(str)
    def load_pdf(self, pdf_path: str) -> None:
        if pdf_path:
            pdf_url = QUrl.fromLocalFile(pdf_path)
            if pdf_url.isValid():
                self.web_view.setUrl(QUrl.fromLocalFile(pdf_path))
            else:
                pass


class QuiltToggleableWidget(QWidget):
    """A base class for toggleable widgets that can be shown or hidden."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("toggleable-widget")

    @Slot(bool)
    def toggle(self, visible: bool):
        if visible:
            self.show()
        else:
            self.hide()


class QuiltNavigationPane(QWidget):
    state = True

    def __init__(self, parent: Optional[QWidget] = None, workspace: Optional[QuiltWorkspace] = None,
                 tree: Optional[QuiltTreeView] = None):
        super().__init__(parent)

        self.parent = parent
        self.workspace = workspace
        self.tree = tree

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar 
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))  # Optional
        toolbar.setMovable(False)
        toolbar.setFloatable(False)

        # Spacers
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        left_action = QWidgetAction(self)
        left_action.setDefaultWidget(left_spacer)
        
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        right_action = QWidgetAction(self)
        right_action.setDefaultWidget(right_spacer)
        toolbar.addAction(right_action)

        # Add placeholder tool buttons
        btn_bookmark = QToolButton(self)
        btn_bookmark.setIcon(QIcon(load_icon("bookmarks")))
        btn_bookmark.setToolTip("Bookmarks")
        btn_bookmark.setObjectName("toolbar-button")

        # Adding tools to the toolbar
        toolbar.addAction(left_action)
        toolbar.addWidget(btn_bookmark)
        toolbar.addAction(right_action)

        # Add widgets to the layout
        layout.addWidget(toolbar)
        layout.addWidget(tree)

        # Set the navigation pane layout
        self.setLayout(layout)
        self.setObjectName("navigation-pane")
        self.setMinimumSize(350, 0)

    @Slot(bool)
    def toggle(self, visible):
        if visible:
            self.show()
        else:
            # Hide the navigation pane
            self.hide()
            #self.parent.setSizes([0, 1])


class QuiltViewPane(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.parent = parent

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add widgets to the layout
        #if pdf_viewer is not None:
        #    layout.addWidget(pdf_viewer)
    
        # Set the view pane layout
        self.setLayout(layout)
        self.setObjectName("view-pane")
        self.setMinimumSize(350, 0)


class QuiltFeaturePane(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.parent = parent

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Set the feature pane layout
        self.setLayout(layout)
        self.setObjectName("feature-pane")
        self.setMinimumSize(350, 0)

    @Slot(bool)
    def toggle(self, visible):
        if visible:
            self.show()
        else:
            # Hide the navigation pane
            self.hide()
            #self.parent.setSizes([0, 1])


class QuiltStartView(QWidget):
    signal_new_workspace = Signal()
    signal_open_workspace = Signal()
    signal_open_settings = Signal()

    def __init__(self, parent: Optional[QWidget] = None, quilt_style = None):
        super().__init__(parent)
        self.parent = parent

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
        btn_new.clicked.connect(self._new_workspace)
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
        v_layout = QVBoxLayout(self)
        v_layout.addStretch(1) 
        v_layout.addLayout(h_layout)
        v_layout.addStretch(1)

        self.setLayout(v_layout)
        self.setObjectName("start-view")

    def _new_workspace(self):
        self.signal_new_workspace.emit()

    def _open_workspace(self):
        self.signal_open_workspace.emit()

    def _open_settings(self):
        self.signal_open_settings.emit()


class QuiltMainView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None, workspace: Optional[QuiltWorkspace] = None,
                 quilt_style = None):
        super().__init__(parent)
        self.parent = parent
        self.workspace = workspace
        self.quilt_style = quilt_style

        # Build necessary components
        self._build_navigation_tree()

        # Setup widget signaling
        #self.tree.pdf_selected.connect(self.pdf_viewer.load_pdf)

        # Create horizontal splitter
        self.main_splitter = HoverAwareSplitter(Qt.Horizontal)

        # Create panes
        self.navigation_pane = QuiltNavigationPane(self.main_splitter, self.workspace, self.tree)
        self.view_pane = QuiltViewPane(self.main_splitter)
        self.feature_pane = QuiltFeaturePane(self.main_splitter)

        # Set object names for styling
        self.view_pane.setObjectName("view-pane")
        self.feature_pane.setObjectName("feature-pane")

        # Add panes to the main splitter
        self.main_splitter.addWidget(self.navigation_pane)
        self.main_splitter.addWidget(self.view_pane)
        self.main_splitter.addWidget(self.feature_pane)

        # Set initial size ratios
        self.main_splitter.setSizes([100, 200, 100])

        # Set minimum sizes for panes
        self.view_pane.setMinimumSize(100, 0)
        self.feature_pane.setMinimumSize(350, 0)

        # Make sure panels are not collapsible
        self.main_splitter.setCollapsible(0, False)  # Navigation pane
        self.main_splitter.setCollapsible(1, False)  # View pane
        self.main_splitter.setCollapsible(2, False)  # Feature pane

        # Mouse tracking for the handles of the splitter
        for i in range(self.main_splitter.count()):
            handle = self.main_splitter.handle(i)
            handle.setMouseTracking(True)
            handle.setCursor(Qt.SizeHorCursor)

        # Create the main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.main_splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.setLayout(layout)
        self.setObjectName("main-view")
    
    def _build_navigation_tree(self):
        # Navigation tree
        model = QuiltFileSystemModel(self)
        model.setRootPath(self.workspace.workspace_dir)
        model.setNameFilters(["*.pdf", "*.md", "*.png", "*.jpg", "*.jpeg", "*.gif"])
        model.setNameFilterDisables(False)

        caret_down_path = load_and_save_padded_icon("caret-down", padding=12)
        caret_right_path = load_and_save_padded_icon("caret-right", padding=12)
        caret_style = f"""
            QTreeView#navigation-tree::branch:closed:has-children {{
                image: url({caret_right_path});
            }}

            QTreeView#navigation-tree::branch:open:has-children {{
                image: url({caret_down_path});
            }}
            """
        full_style_sheet = self.quilt_style + caret_style
        self.tree = QuiltTreeView(self, model, self.workspace, full_style_sheet)


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