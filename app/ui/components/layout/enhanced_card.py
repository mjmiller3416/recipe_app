"""
Enhanced Card Widget - Modern, Flexible Card Component

A comprehensive card widget that supports:
- Flexible header composition (title, subtitle, avatar, actions)
- Media area for images/videos
- Multiple content sections
- Action buttons in footer
- State management (expanded/collapsed, selected)
- Fluent API for easy construction
"""

from typing import Optional, Union, List
from enum import Enum

from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, 
    QWidget, QScrollArea, QButtonGroup, QSpacerItem
)
from PySide6.QtGui import QPixmap, QFont

from app.ui.components.widgets.button import Button, ToolButton
from app.ui.components.widgets.circular_image import CircularImage
from app.style.theme.config import Qss
from app.style.theme_controller import Theme
from app.style.effects import Effects, Shadow
from app.style.icon.config import Name, Type


class CardState(Enum):
    """Card state enumeration."""
    NORMAL = "normal"
    SELECTED = "selected"
    DISABLED = "disabled"


class CardSize(Enum):
    """Predefined card sizes."""
    COMPACT = (320, None)    # Fixed width, auto height - increased from 280
    MEDIUM = (400, None)     # Fixed width, auto height - increased from 340
    LARGE = (480, None)      # Fixed width, auto height - increased from 400
    WIDE = (600, None)       # Wide card for more content
    FULL_WIDTH = (None, None)  # Fill parent width


class EnhancedCard(QFrame):
    """
    Enhanced card widget with comprehensive features and fluent API.
    
    Features:
    - Flexible header with title, subtitle, avatar, and action buttons
    - Optional media area for images/videos
    - Multiple content sections
    - Footer with action buttons
    - Expandable/collapsible content
    - Selection state management
    - Fluent builder API
    
    Usage:
        card = (EnhancedCard()
                .set_title("Recipe Card")
                .set_subtitle("Delicious homemade pasta")
                .set_avatar("/path/to/image.jpg")
                .add_header_action("favorite", Name.HEART)
                .add_media_image("/path/to/recipe.jpg")
                .add_content_text("This is a delicious recipe...")
                .add_action_button("View Recipe", Name.VIEW)
                .set_size(CardSize.MEDIUM))
    """
    
    # Signals
    clicked = Signal()
    selection_changed = Signal(bool)
    expanded_changed = Signal(bool)
    action_clicked = Signal(str)  # Action name
    
    def __init__(self, parent=None):
        """Initialize the enhanced card widget."""
        super().__init__(parent)
        
        # Register for styling
        Theme.register_widget(self, Qss.CARD)
        
        # Configure frame
        self.setObjectName("EnhancedCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("card_state", CardState.NORMAL.value)
        
        # State management
        self._state = CardState.NORMAL
        self._is_expandable = False
        self._is_expanded = True
        self._is_selectable = False
        self._is_selected = False
        
        # Internal components
        self._avatar = None
        self._title_label = None
        self._subtitle_label = None
        self._media_widget = None
        self._header_actions = {}
        self._action_buttons = {}
        self._content_sections = []
        
        # Default sizes
        self._default_header_icon_size = 24
        self._default_action_icon_size = 16
        
        # Layouts
        self._setup_layout()
        
        # Default styling - use Preferred to allow better expansion
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        Effects.apply_shadow(self, Shadow.ELEVATION_12)
        
    def _setup_layout(self):
        """Setup the card's layout structure."""
        # Main layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # Header section
        self._header_frame = QFrame()
        self._header_frame.setObjectName("CardHeader")
        self._header_layout = QHBoxLayout(self._header_frame)
        self._header_layout.setContentsMargins(16, 16, 16, 12)
        self._header_layout.setSpacing(12)
        
        # Header content (avatar + text) - allow it to expand
        self._header_content = QHBoxLayout()
        self._header_content.setSpacing(12)
        self._header_layout.addLayout(self._header_content, 1)  # Give it stretch factor
        
        # Header actions - keep compact
        self._header_actions_layout = QHBoxLayout()
        self._header_actions_layout.setSpacing(4)
        self._header_layout.addLayout(self._header_actions_layout)
        
        self._main_layout.addWidget(self._header_frame)
        
        # Media section (hidden by default)
        self._media_frame = QFrame()
        self._media_frame.setObjectName("CardMedia") 
        self._media_frame.hide()
        self._media_layout = QVBoxLayout(self._media_frame)
        self._media_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.addWidget(self._media_frame)
        
        # Content section
        self._content_frame = QFrame()
        self._content_frame.setObjectName("CardContent")
        self._content_layout = QVBoxLayout(self._content_frame)
        self._content_layout.setContentsMargins(16, 12, 16, 16)
        self._content_layout.setSpacing(12)
        self._main_layout.addWidget(self._content_frame)
        
        # Actions section (hidden by default)
        self._actions_frame = QFrame()
        self._actions_frame.setObjectName("CardActions")
        self._actions_frame.hide()
        self._actions_layout = QHBoxLayout(self._actions_frame)
        self._actions_layout.setContentsMargins(16, 8, 16, 16)
        self._actions_layout.setSpacing(8)
        self._main_layout.addWidget(self._actions_frame)
        
    # ── Fluent API Methods ──────────────────────────────────────────────────────────────────────
    
    def set_title(self, title: str, font_size: int = 18) -> 'EnhancedCard':
        """Set the card title."""
        if not self._title_label:
            self._title_label = QLabel()
            self._title_label.setObjectName("CardTitle")
            self._title_label.setWordWrap(True)  # Enable word wrapping
            self._title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            self._header_content.addWidget(self._title_label)
        
        self._title_label.setText(title)
        font = self._title_label.font()
        font.setPointSize(font_size)
        font.setBold(True)
        self._title_label.setFont(font)
        return self
        
    def set_subtitle(self, subtitle: str, font_size: int = 14) -> 'EnhancedCard':
        """Set the card subtitle."""
        if not self._subtitle_label:
            # Create text container if title exists
            if self._title_label:
                # Wrap title in container if not already
                if self._title_label.parent() == self._header_frame:
                    text_container = QVBoxLayout()
                    text_container.setSpacing(4)
                    self._header_content.removeWidget(self._title_label)
                    text_container.addWidget(self._title_label)
                    self._header_content.addLayout(text_container)
                    self._text_container = text_container
                else:
                    self._text_container = self._title_label.parent().layout()
            else:
                self._text_container = QVBoxLayout()
                self._text_container.setSpacing(4)
                self._header_content.addLayout(self._text_container)
            
            self._subtitle_label = QLabel()
            self._subtitle_label.setObjectName("CardSubtitle")
            self._subtitle_label.setWordWrap(True)  # Enable word wrapping
            self._subtitle_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            self._text_container.addWidget(self._subtitle_label)
        
        self._subtitle_label.setText(subtitle)
        font = self._subtitle_label.font()
        font.setPointSize(font_size)
        self._subtitle_label.setFont(font)
        return self
        
    def set_avatar(self, image_path: str, size: int = 40) -> 'EnhancedCard':
        """Set an avatar image in the header."""
        if not self._avatar:
            self._avatar = CircularImage(size, size)
            # Insert at beginning of header content
            self._header_content.insertWidget(0, self._avatar)
        
        self._avatar.load_image(image_path)
        return self
        
    def add_header_action(self, action_name: str, icon: Name, tooltip: str = "", 
                         icon_size: int = None) -> 'EnhancedCard':
        """Add an action button to the header.
        
        Args:
            action_name: Unique identifier for the action
            icon: Icon to display
            tooltip: Optional tooltip text
            icon_size: Size of the icon in pixels (uses default if None)
        """
        if icon_size is None:
            icon_size = self._default_header_icon_size
            
        action_btn = ToolButton(Type.SECONDARY, icon)
        action_btn.setStateIconSize(icon_size, icon_size)
        action_btn.setToolTip(tooltip)
        action_btn.clicked.connect(lambda: self.action_clicked.emit(action_name))
        
        self._header_actions[action_name] = action_btn
        self._header_actions_layout.addWidget(action_btn)
        return self
        
    def add_media_image(self, image_path: str, max_height: int = 200) -> 'EnhancedCard':
        """Add an image to the media section."""
        if not self._media_widget:
            self._media_widget = QLabel()
            self._media_widget.setObjectName("CardMediaImage")
            self._media_widget.setScaledContents(True)
            self._media_widget.setMaximumHeight(max_height)
            self._media_layout.addWidget(self._media_widget)
            self._media_frame.show()
        
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self._media_widget.setPixmap(pixmap)
        return self
        
    def add_content_text(self, text: str, font_size: int = 14) -> 'EnhancedCard':
        """Add text content to the card."""
        text_label = QLabel(text)
        text_label.setObjectName("CardContentText")
        text_label.setWordWrap(True)
        
        font = text_label.font()
        font.setPointSize(font_size)
        text_label.setFont(font)
        
        self._content_layout.addWidget(text_label)
        self._content_sections.append(text_label)
        return self
        
    def add_content_widget(self, widget: QWidget) -> 'EnhancedCard':
        """Add a custom widget to the content area."""
        self._content_layout.addWidget(widget)
        self._content_sections.append(widget)
        return self
        
    def add_action_button(self, text: str, icon: Name = None, action_name: str = None,
                         icon_size: int = None) -> 'EnhancedCard':
        """Add an action button to the footer."""
        if action_name is None:
            action_name = text.lower().replace(" ", "_")
        if icon_size is None:
            icon_size = self._default_action_icon_size
            
        action_btn = Button(text, Type.PRIMARY, icon)
        if icon:
            action_btn.setStateIconSize(icon_size, icon_size)
        action_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # Allow expansion
        action_btn.clicked.connect(lambda: self.action_clicked.emit(action_name))
        
        self._action_buttons[action_name] = action_btn
        self._actions_layout.addWidget(action_btn)
        self._actions_frame.show()
        return self
        
    def add_secondary_action(self, text: str, icon: Name = None, action_name: str = None,
                           icon_size: int = None) -> 'EnhancedCard':
        """Add a secondary action button to the footer.""" 
        if action_name is None:
            action_name = text.lower().replace(" ", "_")
        if icon_size is None:
            icon_size = self._default_action_icon_size
            
        action_btn = Button(text, Type.SECONDARY, icon)
        if icon:
            action_btn.setStateIconSize(icon_size, icon_size)
        action_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # Allow expansion
        action_btn.clicked.connect(lambda: self.action_clicked.emit(action_name))
        
        self._action_buttons[action_name] = action_btn
        self._actions_layout.addWidget(action_btn)
        self._actions_frame.show()
        return self
        
    def set_size(self, size: CardSize) -> 'EnhancedCard':
        """Set the card size."""
        width, height = size.value
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        return self
        
    def set_expandable(self, expandable: bool = True, initially_expanded: bool = True) -> 'EnhancedCard':
        """Make the card expandable/collapsible."""
        self._is_expandable = expandable
        self._is_expanded = initially_expanded
        
        if expandable:
            # Add expand/collapse button to header
            expand_icon = Name.ANGLE_DOWN if initially_expanded else Name.ANGLE_DOWN  # You might want a right-pointing arrow
            self.add_header_action("expand", expand_icon, "Expand/Collapse")
            
        return self
        
    def set_selectable(self, selectable: bool = True) -> 'EnhancedCard':
        """Make the card selectable."""
        self._is_selectable = selectable
        if selectable:
            self.mousePressEvent = self._handle_selection_click
        return self
        
    # ── State Management ────────────────────────────────────────────────────────────────────────
    
    def set_selected(self, selected: bool):
        """Set the selection state."""
        if not self._is_selectable:
            return
            
        if self._is_selected != selected:
            self._is_selected = selected
            self.setProperty("card_state", CardState.SELECTED.value if selected else CardState.NORMAL.value)
            self.style().unpolish(self)
            self.style().polish(self)
            self.selection_changed.emit(selected)
            
    def is_selected(self) -> bool:
        """Check if card is selected."""
        return self._is_selected
        
    def set_expanded(self, expanded: bool, animate: bool = True):
        """Set the expanded state.""" 
        if not self._is_expandable or self._is_expanded == expanded:
            return
            
        self._is_expanded = expanded
        
        if animate:
            # Animate content visibility
            self._animate_expand(expanded)
        else:
            self._content_frame.setVisible(expanded)
            
        # Update expand button icon
        if "expand" in self._header_actions:
            expand_btn = self._header_actions["expand"]
            # Update icon based on state (you'd need to implement icon changing)
            
        self.expanded_changed.emit(expanded)
        
    def _animate_expand(self, expand: bool):
        """Animate the expand/collapse transition."""
        # This would implement smooth height animation
        # For now, just show/hide
        self._content_frame.setVisible(expand)
        
    def _handle_selection_click(self, event):
        """Handle click for selection."""
        if self._is_selectable:
            self.set_selected(not self._is_selected)
        super().mousePressEvent(event)
        
    # ── Utility Methods ─────────────────────────────────────────────────────────────────────────
    
    def get_header_action(self, action_name: str) -> Optional[ToolButton]:
        """Get a header action button by name."""
        return self._header_actions.get(action_name)
        
    def get_action_button(self, action_name: str) -> Optional[Button]:
        """Get an action button by name."""
        return self._action_buttons.get(action_name)
        
    def clear_content(self):
        """Clear all content from the card."""
        for section in self._content_sections:
            section.deleteLater()
        self._content_sections.clear()
        
    def hide_header(self):
        """Hide the header section."""
        self._header_frame.hide()
        
    def show_header(self):
        """Show the header section."""
        self._header_frame.show()
        
    def set_content_padding(self, left: int, top: int, right: int, bottom: int):
        """Set content area padding."""
        self._content_layout.setContentsMargins(left, top, right, bottom)
        
    def set_minimum_width(self, width: int) -> 'EnhancedCard':
        """Set minimum width to prevent text clipping.
        
        Args:
            width: Minimum width in pixels
        """
        self.setMinimumWidth(width)
        return self
        
    def enable_text_wrapping(self, enabled: bool = True) -> 'EnhancedCard':
        """Enable or disable text wrapping for title and subtitle.
        
        Args:
            enabled: Whether to enable text wrapping
        """
        if self._title_label:
            self._title_label.setWordWrap(enabled)
        if self._subtitle_label:
            self._subtitle_label.setWordWrap(enabled)
        return self
        
    def set_header_padding(self, left: int, top: int, right: int, bottom: int) -> 'EnhancedCard':
        """Set header area padding.
        
        Args:
            left, top, right, bottom: Padding in pixels
        """
        self._header_layout.setContentsMargins(left, top, right, bottom)
        return self
        
    def set_default_header_icon_size(self, size: int) -> 'EnhancedCard':
        """Set the default icon size for header action buttons.
        
        Args:
            size: Icon size in pixels
            
        Note: This only affects new header actions added after this call.
        Use update_header_icon_sizes() to resize existing buttons.
        """
        self._default_header_icon_size = size
        return self
        
    def set_default_action_icon_size(self, size: int) -> 'EnhancedCard':
        """Set the default icon size for footer action buttons.
        
        Args:
            size: Icon size in pixels
            
        Note: This only affects new action buttons added after this call.
        Use update_action_icon_sizes() to resize existing buttons.
        """
        self._default_action_icon_size = size
        return self
        
    def update_header_icon_sizes(self, size: int) -> 'EnhancedCard':
        """Update the icon size for all existing header action buttons.
        
        Args:
            size: New icon size in pixels
        """
        for action_btn in self._header_actions.values():
            action_btn.setStateIconSize(size, size)
        return self
        
    def update_action_icon_sizes(self, size: int) -> 'EnhancedCard':
        """Update the icon size for all existing footer action buttons.
        
        Args:
            size: New icon size in pixels
        """
        for action_btn in self._action_buttons.values():
            if hasattr(action_btn, 'setStateIconSize'):  # Check if it has an icon
                action_btn.setStateIconSize(size, size)
        return self
        
    def set_header_action_icon_size(self, action_name: str, size: int) -> 'EnhancedCard':
        """Set the icon size for a specific header action button.
        
        Args:
            action_name: Name of the header action
            size: New icon size in pixels
        """
        action_btn = self._header_actions.get(action_name)
        if action_btn:
            action_btn.setStateIconSize(size, size)
        return self


# ── Convenience Functions ───────────────────────────────────────────────────────────────────────

def create_simple_card(title: str, content: str = "", size: CardSize = CardSize.MEDIUM) -> EnhancedCard:
    """Create a simple card with just title and content."""
    card = EnhancedCard().set_title(title).set_size(size)
    if content:
        card.add_content_text(content)
    return card


def create_profile_card(name: str, bio: str, avatar_path: str = None) -> EnhancedCard:
    """Create a profile card with avatar, name and bio."""
    card = EnhancedCard().set_title(name).set_subtitle(bio).set_size(CardSize.MEDIUM)
    if avatar_path:
        card.set_avatar(avatar_path)
    return card


def create_media_card(title: str, description: str, image_path: str, 
                     action_text: str = "View") -> EnhancedCard:
    """Create a media card with image, title, description and action."""
    return (EnhancedCard()
            .set_title(title)
            .add_media_image(image_path)
            .add_content_text(description)
            .add_action_button(action_text)
            .set_size(CardSize.MEDIUM))