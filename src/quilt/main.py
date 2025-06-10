import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import *

from src.quilt.ui.colors import COLORS
from src.quilt.ui.utils import load_icon, load_colored_icon, load_and_save_padded_icon
from src.quilt.ui.widgets import QuiltTitleBar, QuiltFileSystemModel, QuiltTreeItemDelegate
from src.quilt.workspace import QuiltWorkspace

def load_stylesheet(style_name):
    with open(f'styles/{style_name}.qss', 'r') as file:
        return file.read()

class QuiltMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quilt Application")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Set window icon
        self.setWindowIcon(QIcon("assets/quilt.ico"))

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

    def _build_main_layout(self):
        # Create panes
        self.navigation_pane = self._build_navigation_pane()
        self.view_pane = QWidget()
        self.feature_pane = QWidget(self)

        # Set object names for styling
        self.navigation_pane.setObjectName("navigation-pane")
        self.view_pane.setObjectName("view-pane")
        self.feature_pane.setObjectName("feature-pane")

        # Create horizontal splitter
        h_splitter = QSplitter(Qt.Horizontal)
        h_splitter.addWidget(self.navigation_pane)
        h_splitter.addWidget(self.view_pane)
        h_splitter.addWidget(self.feature_pane)

        # Set initial size ratios
        h_splitter.setSizes([100, 200, 100])

        # Set minimum sizes for panes
        self.navigation_pane.setMinimumSize(350, 0)
        self.view_pane.setMinimumSize(100, 0)
        self.feature_pane.setMinimumSize(350, 0)

        # Make sure panels are not collapsible
        h_splitter.setCollapsible(0, False)  # Navigation pane
        h_splitter.setCollapsible(1, False)  # View pane
        h_splitter.setCollapsible(2, False)  # Feature pane

        # Create container
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(h_splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        container.setLayout(layout)

        # Return the main layout
        return container

    def _build_navigation_pane(self):
        navigation_pane = QWidget()
        layout = QVBoxLayout(navigation_pane)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # -------- Top toolbar --------
        top_toolbar = QToolBar()
        top_toolbar.setIconSize(QSize(16, 16))  # Optional
        top_toolbar.setMovable(False)
        top_toolbar.setFloatable(False)

        # Add placeholder tool buttons
        tool_btn_1 = QToolButton()
        tool_btn_1.setText("🔍")
        tool_btn_1.setToolTip("Search")

        tool_btn_2 = QToolButton()
        tool_btn_2.setText("➕")
        tool_btn_2.setToolTip("Add")

        top_toolbar.addWidget(tool_btn_1)
        top_toolbar.addWidget(tool_btn_2)

        # -------- TreeView (middle) --------
        model = QuiltFileSystemModel()
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

        tree = QTreeView()
        tree.setObjectName("navigation-tree")
        tree.setModel(model)
        tree.setRootIndex(model.index(self.workspace.workspace_dir))
        tree.setHeaderHidden(True)
        tree.setFocusPolicy(Qt.NoFocus)  # Disable focus outline
        tree.hideColumn(1)  # Size
        tree.hideColumn(2)  # Type
        tree.hideColumn(3)  # Last Modified
        tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tree.setItemDelegate(QuiltTreeItemDelegate())  # Use custom delegate to prevent icon tinting
        tree.setStyleSheet(full_style_sheet)  # Apply the full stylesheet

        # -------- Bottom toolbar --------
        bottom_toolbar = QToolBar()
        bottom_toolbar.setIconSize(QSize(16, 16))
        bottom_toolbar.setMovable(False)
        bottom_toolbar.setFloatable(False)

        bottom_btn = QToolButton()
        bottom_btn.setText("⚙")
        bottom_btn.setToolTip("Settings")

        bottom_toolbar.addWidget(bottom_btn)

        # -------- Add to layout --------
        layout.addWidget(top_toolbar)
        layout.addWidget(tree)
        layout.addWidget(bottom_toolbar)

        # Add the layout to the navigation pane
        navigation_pane.setLayout(layout)
        navigation_pane.setObjectName("navigation-pane")

        return navigation_pane

    def _build_view_pane(self):
        pass

    def _build_feature_pane(self):
        pass

    def _build_not_implemented_popup(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Not Implemented")
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)    

        # ---- Custom container with rounded background ----
        container = QWidget()
        container.setObjectName("unimplemented-container")

        # ---- Icon and message ----
        icon = QIcon(load_colored_icon("warning-circle", "dark-red"))
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(32, 32))
        icon_label.setAlignment(Qt.AlignTop)

        text_label = QLabel("This feature is not implemented yet.")
        text_label.setWordWrap(False)
        text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        message_layout = QHBoxLayout()
        message_layout.addWidget(icon_label)
        message_layout.addWidget(text_label)

        # ---- OK button ----
        ok_button = QPushButton("OK")
        ok_button.setObjectName("unimplemented-button")
        ok_button.clicked.connect(dialog.accept)
        ok_button.setFixedWidth(80)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()

        # ---- Combine in custom container ----
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addLayout(message_layout)
        layout.addSpacing(15)
        layout.addLayout(button_layout)

        # ---- Top-level layout ----
        top_layout = QVBoxLayout(dialog)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(container)

        # Temporarily hide the 

        dialog.setLayout(top_layout)
        dialog.exec()

    def _create_workspace(self):
        self._build_not_implemented_popup()

    def _open_workspace(self):
        # Open a file dialog to select a workspace
        workspace_dir = QFileDialog.getExistingDirectory(self, "Open Workspace")
        if workspace_dir:
            self.workspace = QuiltWorkspace(workspace_dir)

            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(QuiltTitleBar(self))
            layout.addWidget(self._build_main_layout())

            # Central widget
            central = QWidget()
            central.setLayout(layout)
            central.setStyleSheet(self.quilt_style)
            self.setCentralWidget(central)

    def _open_settings(self):
        self._build_not_implemented_popup()


def main():
    app = QApplication(sys.argv)
    quilt = QuiltMainWindow()
    quilt.show()
    sys.exit(app.exec())