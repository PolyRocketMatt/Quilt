from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import *

from src.quilt.ui.utils import load_icon, load_favicon

class QuiltTitleBar(QWidget):
    def __init__(self, parent=None, title=" Quilt"):
        super().__init__(parent)
        self.parent = parent
        self.title = title
        self.setObjectName("title-bar")
        self.setFixedHeight(32)
        self._init_ui()

        self._start_pos = None
        self._is_dragging = False

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        favicon = load_favicon()
        favicon.setObjectName("favicon")
        title = QLabel(self.title)

        btn_minimize = QPushButton(QIcon(load_icon("minus")), "")
        btn_minimize.setObjectName("title-bar-button")
        btn_minimize.setToolTip("Minimize")
        btn_minimize.clicked.connect(self.parent.showMinimized)

        btn_restore = QPushButton("")
        btn_restore.setObjectName("title-bar-button")
        if self.parent.isMaximized():
            btn_restore.setIcon(QIcon(load_icon("frame-corners")))
            btn_restore.setToolTip("Restore")
            btn_restore.clicked.connect(self.toggle_state)
        else:
            btn_restore.setIcon(QIcon(load_icon("square")))
            btn_restore.setToolTip("Maximize")
            btn_restore.clicked.connect(self.toggle_state)

        btn_close = QPushButton(QIcon(load_icon("x")), "")
        btn_close.setObjectName("title-bar-close-button")
        btn_close.setToolTip("Close")
        btn_close.clicked.connect(self.parent.close)

        layout.addWidget(favicon)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(btn_minimize)
        layout.addWidget(btn_restore)
        layout.addWidget(btn_close)
        self.setLayout(layout)

    def toggle_state(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.sender().setIcon(QIcon(load_icon("square")))
            self.sender().setToolTip("Maximize")
        else:
            self.parent.showMaximized()
            self.sender().setIcon(QIcon(load_icon("frame-corners")))
            self.sender().setToolTip("Restore")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_pos = event.globalPosition().toPoint()
            self._is_dragging = True
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            # Calculate the offset
            current_pos = event.globalPosition().toPoint()
            offset = current_pos - self._start_pos
            self._start_pos = current_pos

            # Move the window
            self.window().move(self.window().pos() + offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            event.accept()


class QuiltFileSystemModel(QFileSystemModel):
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DecorationRole and index.column() == 0:
            file_path = self.filePath(index)
            if file_path.endswith(".pdf"):
                return QIcon(load_icon("file-pdf"))
            elif file_path.endswith(".md"):
                return QIcon(load_icon("file-markdown"))
            elif file_path.endswith((".png", ".jpg", ".jpeg", ".gif")):
                return QIcon(load_icon("file-image"))
            
            # If the file is a directory, return a folder icon
            if self.isDir(index):
                return QIcon(load_icon("folder"))
        return super().data(index, role)
        
class QuiltTreeItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option_copy = QStyleOptionViewItem(option)
        
        # Still draw the highlighted background
        if option.state & QStyle.State_Selected:
            style = option.widget.style()
            style.drawPrimitive(QStyle.PE_PanelItemViewItem, option, painter, option.widget)

        # Make text bold when selected
        if option.state & QStyle.State_Selected or option.state & QStyle.State_MouseOver:
            option_copy.font.setBold(True)

        # Use full selected style (so background/text changes still happen)
        # BUT draw the decoration (icon) manually to prevent selection tint
        option_copy.state &= ~QStyle.State_Selected
        super().paint(painter, option_copy, index)
