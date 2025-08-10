"""app/ui/components/widgets/info_card.py

InfoCard component - A vertical info card showing an icon, title, and value.
Used for recipe metadata like total time, servings, category, dietary info.
"""

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from app.style.icon import AppIcon
from app.style.icon.config import Icon


class InfoCard(QWidget):
    """A vertical info card with icon, title, and value for recipe metadata."""
    
    def __init__(self, icon: Icon, title: str, value: str, parent=None):
        super().__init__(parent)
        self.setObjectName("InfoCard")
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icon
        self.icon_widget = AppIcon(icon)
        self.icon_widget.setFixedSize(QSize(24, 24))
        self.icon_widget.setObjectName("InfoCardIcon")
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("InfoCardTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setObjectName("InfoCardValue")
        self.value_label.setAlignment(Qt.AlignCenter)
        
        # Add to layout
        layout.addWidget(self.icon_widget, 0, Qt.AlignCenter)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        
    def setTitle(self, title: str):
        """Update the title text."""
        self.title_label.setText(title)
        
    def setValue(self, value: str):
        """Update the value text."""
        self.value_label.setText(value)
        
    def setIcon(self, icon: Icon):
        """Update the icon."""
        self.icon_widget.setIcon(icon)