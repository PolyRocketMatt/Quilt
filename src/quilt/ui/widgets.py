from typing import Optional

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFileSystemModel,
    QStyledItemDelegate, QStyle, QStyleOptionViewItem
)

from src.quilt.ui.utils import load_icon, load_favicon


class QuiltTitleBar(QWidget):
    """Custom title bar widget for Quilt windows."""

    def __init__(self, parent: Optional[QWidget] = None, title: str = " Quilt"):
        super().__init__(parent)
        self.parent = parent
        self.title = title

        self.setObjectName("title-bar")
        self.setFixedHeight(32)

        self._start_pos: Optional[QPoint] = None
        self._is_dragging = False

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        favicon = load_favicon()
        favicon.setObjectName("favicon")

        title_label = QLabel(self.title)

        self.btn_minimize = self._create_button("minus", "Minimize", self.parent.showMinimized)
        self.btn_restore = self._create_button("", "", self.toggle_state)
        self._update_restore_icon()

        self.btn_close = self._create_button("x", "Close", self.parent.close)
        self.btn_close.setObjectName("title-bar-close-button")

        layout.addWidget(favicon)
        layout.addWidget(title_label)
        layout.addStretch()
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

    def _update_restore_icon(self) -> None:
        if self.parent.isMaximized():
            icon, tooltip = "frame-corners", "Restore"
        else:
            icon, tooltip = "square", "Maximize"

        self.btn_restore.setIcon(QIcon(load_icon(icon)))
        self.btn_restore.setToolTip(tooltip)

    def toggle_state(self) -> None:
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
