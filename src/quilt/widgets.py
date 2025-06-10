from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QObject
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import *

class QuiltFileSystemModel(QFileSystemModel):
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DecorationRole and index.column() == 0:
            file_path = self.filePath(index)
            if file_path.endswith(".pdf"):
                return QIcon("assets/file-pdf-dark.png")
            elif file_path.endswith(".md"):
                return QIcon("assets/file-markdown-dark.png")
            elif file_path.endswith((".png", ".jpg", ".jpeg", ".gif")):
                return QIcon("assets/image-dark.png")
            
            # If the file is a directory, return a folder icon
            if self.isDir(index):
                return QIcon("assets/folder-dark.png")
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
