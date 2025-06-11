from typing import Optional

from PySide6.QtCore import Qt, QSize, QPoint, QUrl, Signal, Slot
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QDialog, 
    QFileSystemModel,
    QHBoxLayout,
    QLabel,
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
    load_icon
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