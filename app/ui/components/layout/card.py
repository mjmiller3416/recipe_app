"""Card layout components for the recipe application.

This module provides a comprehensive set of card-based container widgets designed for
modern UI applications. The cards support various layout types, elevation effects,
theming integration, and interactive elements.

Classes:
    BaseCard: Generic container with elevation effects and flexible layouts
    Card: Standard card widget with header/subheader support
    ActionCard: Card widget with integrated button functionality

The card system is built on top of PySide6 and integrates with the application's
theming system to provide consistent visual styling across the interface.
"""

# ── Imports ──────────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget)

from app.style.effects import Effects, Shadow
from app.style.icon import AppIcon, Name, Type
from app.ui.components.widgets.button import Button

# ── Constants ────────────────────────────────────────────────────────────────────────────────
EXPANDED_HEIGHT = 300    # Full height when expanded
COLLAPSED_HEIGHT = 80    # Height when collapsed (header visible) - increased for more spacing
DURATION = 300           # Animation duration


# ── Base Card Widget ─────────────────────────────────────────────────────────────────────────
class BaseCard(QFrame):
    """A foundational container widget providing elevation effects and flexible layout management.

    BaseCard serves as the core building block for all card-style UI components in the
    application. It automatically handles content scaling, provides configurable margins
    and elevation effects, and supports multiple layout types for content organization.

    The widget integrates with the application's theming system and provides a clean API
    for content management with support for QVBoxLayout, QHBoxLayout, and QGridLayout.

    Attributes:
        _card_type (str): The card's styling type used by the QSS theming system.
        _layout (QVBoxLayout): Main container layout for the card structure.
        _content_layout (QLayout): User-configurable content layout.
        _content_container (QWidget): Container widget for user content.
        _elevation (Shadow): Current elevation effect applied to the card.
        _elevation_enabled (bool): Whether elevation effects are currently enabled.

    Examples:
        Basic card with vertical layout:
        >>> card = BaseCard(parent=main_window)
        >>> card.addWidget(QLabel("Hello World"))

        Card with grid layout:
        >>> card = BaseCard(content_layout="grid")
        >>> card.addWidget(label1, 0, 0)
        >>> card.addWidget(label2, 0, 1)
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        content_layout: str = "vbox",
        card_type: str = "Default",
    ):
        """Initialize the BaseCard widget with specified configuration.

        Sets up the card container with theming integration, elevation effects,
        and the requested content layout type. The card is automatically registered
        with the application's theme system for consistent styling.

        Args:
            parent (QWidget | None): The parent widget for this card. If None,
                the card will be a top-level widget.
            content_layout (str): The layout type for content organization.
                Supported values:
                - "vbox": Vertical box layout (default)
                - "hbox": Horizontal box layout
                - "grid": Grid layout for tabular arrangement
            card_type (str): The styling identifier used by QSS theming.
                Default is "Default" which applies standard card styling.

        Raises:
            ValueError: If an unsupported content_layout type is provided.

        Note:
            The card automatically applies ELEVATION_6 shadow effects unless
            explicitly disabled through enableElevation(False).
        """
        super().__init__(parent)

        # Card properties
        self._card_type = card_type
        self.setProperty("card", card_type)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self._layout: QVBoxLayout | None = None  # Always VBox for main card
        self._content_layout: QLayout | None = None  # User-configurable
        self._content_container: QWidget | None = None


        # Create the main layout
        self._create_main_layout()
        self._create_content_area(content_layout)

    def _create_main_layout(self):
        """Create and configure the main card layout structure.

        Establishes the primary VBoxLayout that serves as the container for all
        card elements including headers, content areas, and footers. This layout
        maintains consistent spacing and margins across the card.

        Args:
            spacing (int): The vertical spacing between card elements in pixels.
                Default is 20px for optimal visual separation.

        Returns:
            QVBoxLayout: The configured main layout instance for the card.

        Note:
            This method sets standard 20px margins on all sides and applies
            the specified spacing between child elements.
        """
        # ── Note ─────────────────────────────────────────────────────────────────────────────
        # Originally spacing argument was passed and defaulted to 20px
        # Additionally, ContentMargins was also set to 20, 20, 20, 20
        # Currently, both are set to 0 for a more compact design -- seems to fix animation issues.

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        return self._layout

    def _create_content_area(self, layout_type: str = "vbox"):
        """Create and configure the content area with the specified layout type.

        Initializes a content container widget with the requested layout manager.
        The content area is where user widgets are placed and managed. This method
        ensures only one content area exists and configures it with appropriate
        spacing and margin settings.

        Args:
            layout_type (str): The type of layout to create for content management.
                Supported types:
                - "vbox": QVBoxLayout for vertical stacking
                - "hbox": QHBoxLayout for horizontal arrangement
                - "grid": QGridLayout for tabular positioning
                Defaults to "vbox" if an invalid type is provided.

        Note:
            The content container has WA_StyledBackground disabled to prevent
            theming conflicts and uses zero margins with 10px spacing for
            optimal content presentation.
        """
        if self._content_container:
            return

        # Create content container
        self._content_container = QWidget(self)
        self._content_container.setAttribute(Qt.WA_StyledBackground, False)

        # Create content layout based on user preference
        layout_map = {
            "hbox": QHBoxLayout,
            "grid": QGridLayout,
            "vbox": QVBoxLayout
        }
        layout_class = layout_map.get(layout_type.strip().lower(), QVBoxLayout)
        self._content_layout = layout_class(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0) # changed from 10 to 0

        # Add content container to main layout
        if self._layout:
            self._layout.addWidget(self._content_container)

    def _refresh_widget_style(self, widget):
        """Force a style refresh on the specified widget.

        This method triggers a complete style recalculation by unpolishing and
        re-polishing the widget. This is necessary when widget properties change
        and the QSS styling needs to be reapplied to reflect the updates.

        Args:
            widget (QWidget): The widget that requires style refreshing.

        Note:
            This is typically called after programmatic changes to widget
            properties that affect QSS selector matching or styling rules.
        """
        widget.style().unpolish(widget)
        widget.style().polish(widget)


# ── Public API ───────────────────────────────────────────────────────────────────────────────
    def addWidget(self, widget: QWidget, *args, **kwargs):
        """Add a widget to the card's content layout.

        Adds the specified widget to the current content layout using the appropriate
        positioning arguments for the layout type. The method handles different
        argument patterns based on whether the content uses grid, box, or other layouts.

        Args:
            widget (QWidget): The widget to add to the content area.
            *args: Variable positional arguments specific to the layout type:
                - QGridLayout: row (int), column (int), rowSpan (int), columnSpan (int)
                - QVBoxLayout/QHBoxLayout: stretch (int)
            **kwargs: Variable keyword arguments specific to the layout type:
                - alignment: Qt.Alignment for widget positioning
                - Additional layout-specific options

        Raises:
            ValueError: If using QGridLayout without providing minimum required
                row and column arguments.

        Examples:
            For vertical/horizontal layouts:
            >>> card.addWidget(my_label)
            >>> card.addWidget(my_button, alignment=Qt.AlignCenter)

            For grid layouts:
            >>> card.addWidget(label, 0, 0)  # row 0, column 0
            >>> card.addWidget(button, 1, 0, 1, 2)  # span 2 columns
        """

        if isinstance(self._content_layout, QGridLayout) and len(args) < 2:
            raise ValueError("Grid layout requires at least row and column arguments")

        self._content_layout.addWidget(widget, *args, **kwargs)

    def removeWidget(self, widget: QWidget):
        """Remove a widget from the card's content layout.

        Removes the specified widget from the content layout and disconnects it
        from the layout management system. The widget itself is not deleted and
        can be reused or added to other layouts.

        Args:
            widget (QWidget): The widget to remove from the content area.

        Note:
            After removal, you may need to call widget.setParent(None) or
            widget.deleteLater() if you want to completely clean up the widget.
        """
        self._content_layout.removeWidget(widget)

    def clear(self):
        """Remove all widgets from the card's content area.

        Clears all widgets from the content layout and properly disposes of them.
        This method safely removes and deletes all child widgets while maintaining
        the card's header and structure.

        Note:
            This only clears the content area - headers, footers, and card structure
            remain intact. All removed widgets are scheduled for deletion.
        """
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def setContentMargins(self, left: int, top: int, right: int, bottom: int):
        """Configure the margins around the content area.

        Sets the internal spacing between the card's border and its content.
        These margins are applied to the content layout and affect all widgets
        within the content area.

        Args:
            left (int): Left margin in pixels.
            top (int): Top margin in pixels.
            right (int): Right margin in pixels.
            bottom (int): Bottom margin in pixels.

        Note:
            This affects only the content area margins, not the card's outer
            margins which are controlled by the main layout (default 20px).
        """
        self._content_layout.setContentsMargins(left, top, right, bottom)

    def setContentSpacing(self, spacing: int):
        """Configure the spacing between content elements.

        Sets the spacing between child widgets within the content layout.
        This controls how much vertical/horizontal space appears between
        adjacent elements in the content area.

        Args:
            spacing (int): Spacing between content elements in pixels.
                A value of 0 removes spacing, while larger values increase
                the visual separation between elements.

        Note:
            The default content spacing is 10px. This setting only affects
            the content area and not the main card layout spacing.
        """
        self._content_layout.setSpacing(spacing)

    # ── Elevation ────────────────────────────────────────────────────────────────────────────
    def setElevation(self, elevation: Shadow):
        """Configure the card's elevation shadow effect.

        Updates the card's shadow effect to the specified elevation level.
        The shadow is only applied if elevation effects are currently enabled.
        This creates visual depth and hierarchy in the interface.

        Args:
            elevation (Shadow): The elevation level from the Shadow enum.
                Higher values create more prominent shadows and greater
                perceived depth from the background surface.

        Note:
            The elevation will only be visually applied if enableElevation(True)
            has been called. The elevation setting is stored regardless of the
            current enabled state.
        """
        self._elevation = elevation
        if self._elevation_enabled:
            Effects.apply_shadow(self, self._elevation)

    def enableElevation(self, enabled: bool = True):
        """Enable or disable the card's elevation shadow effects.

        Controls whether the card displays its shadow elevation effect.
        When disabled, the card appears flat against the background.
        When enabled, the card displays the shadow level set by setElevation().

        Args:
            enabled (bool): Whether to show elevation effects. Defaults to True.
                - True: Apply the current elevation shadow effect
                - False: Remove all shadow effects (ELEVATION_0)

        Note:
            Disabling elevation improves performance slightly and can be useful
            for cards that don't require visual depth separation.
        """
        self._elevation_enabled = enabled
        Effects.apply_shadow(self, self._elevation if enabled else Shadow.ELEVATION_0)

    # ── Expansion ────────────────────────────────────────────────────────────────────────────
    def expandWidth(self, expand: bool = True):
        """Configure horizontal expansion behavior of the card.

        Controls whether the card expands horizontally to fill available space
        or maintains its preferred width based on content. This affects how
        the card behaves within parent layouts.

        Args:
            expand (bool): Whether to enable horizontal expansion. Defaults to True.
                - True: Card expands to fill available horizontal space
                - False: Card maintains preferred width based on content

        Note:
            The vertical size policy remains unchanged. Use expandHeight() or
            expandBoth() to control vertical expansion behavior.
        """
        policy = self.sizePolicy()
        self.setSizePolicy(
            QSizePolicy.Expanding if expand else QSizePolicy.Preferred,
            policy.verticalPolicy()
        )

    def expandHeight(self, expand: bool = True):
        """Configure vertical expansion behavior of the card.

        Controls whether the card expands vertically to fill available space
        or maintains its preferred height based on content. This affects how
        the card behaves within parent layouts.

        Args:
            expand (bool): Whether to enable vertical expansion. Defaults to True.
                - True: Card expands to fill available vertical space
                - False: Card maintains preferred height based on content

        Note:
            The horizontal size policy remains unchanged. Use expandWidth() or
            expandBoth() to control horizontal expansion behavior.
        """
        policy = self.sizePolicy()
        self.setSizePolicy(
            policy.horizontalPolicy(),
            QSizePolicy.Expanding if expand else QSizePolicy.Preferred
        )

    def expandBoth(self, expand: bool = True):
        """Configure expansion behavior in both horizontal and vertical directions.

        Controls whether the card expands to fill all available space in both
        dimensions or maintains its preferred size based on content. This is
        a convenience method for setting both width and height policies together.

        Args:
            expand (bool): Whether to enable expansion in both directions.
                Defaults to True.
                - True: Card expands to fill all available space
                - False: Card maintains preferred size based on content

        Note:
            This method sets the same policy for both horizontal and vertical
            directions. Use expandWidth() and expandHeight() separately if you
            need different behaviors for each dimension.
        """
        policy = QSizePolicy.Expanding if expand else QSizePolicy.Preferred
        self.setSizePolicy(policy, policy)

    def setFixedPolicy(self):
        """Configure the card to use fixed sizing based on its content.

        Sets both horizontal and vertical size policies to Fixed, meaning the
        card will maintain its minimum size requirements and will not expand
        to fill additional space. The card will size itself based solely on
        its content dimensions.

        Returns:
            BaseCard: Returns self for method chaining.

        Note:
            This is useful for cards that should maintain consistent dimensions
            regardless of available layout space, such as toolbars or status cards.
        """
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return self

class Card(BaseCard):
    """A standard card widget with support for headers, subheaders, and icons.

    Card extends BaseCard to provide structured content presentation with optional
    header sections. It includes support for main headers with icons, subheaders,
    and maintains all the layout and elevation capabilities of the base card.

    This class is ideal for displaying structured information with clear visual
    hierarchy through header sections while maintaining the flexible content
    area provided by BaseCard.

    Attributes:
        _header_container (QWidget): Container for all header elements.
        _header_main_layout (QVBoxLayout): Main layout for header organization.
        _header_row_layout (QHBoxLayout): Layout for header text and icon.
        _header_label (QLabel): Main header text label.
        _header_icon_widget (QWidget): Icon widget displayed with header.
        _subheader_label (QLabel): Optional subheader text label.
        _button_alignment (Qt.Alignment): Alignment setting for footer buttons.

    Examples:
        Basic card with header:
        >>> card = Card()
        >>> card.setHeader("Recipe Details")
        >>> card.addWidget(QLabel("Cooking time: 30 minutes"))

        Card with header and icon:
        >>> card = Card()
        >>> card.setHeader("Shopping List", icon=Name.SHOPPING_CART)
        >>> card.setSubHeader("5 items remaining")
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        content_layout: str = "vbox",
        card_type: str = "Default",
    ):
        """Initialize the Card widget with header support.

        Creates a Card instance that extends BaseCard functionality with support
        for header sections including main headers, subheaders, and icons. The
        card maintains all layout and theming capabilities of BaseCard.

        Args:
            parent (QWidget | None): The parent widget for this card. If None,
                the card will be a top-level widget.
            content_layout (str): The layout type for content organization.
                Inherited from BaseCard - supports "vbox", "hbox", and "grid".
            card_type (str): The styling identifier used by QSS theming.
                Default is "Default" for standard card appearance.

        Note:
            Header components are created on-demand when header methods are called,
            optimizing memory usage for cards that don't require headers.
        """
        super().__init__(parent, content_layout, card_type)

        self.setObjectName("Card")

        # Header/Footer components
        self._header_container:   QWidget     | None = None
        self._header_main_layout: QVBoxLayout | None = None
        self._header_row_layout:  QHBoxLayout | None = None
        self._header_label:       QLabel      | None = None
        self._header_icon_widget: QWidget     | None = None
        self._subheader_label:    QLabel      | None = None

        self._button_alignment = Qt.AlignCenter

        self._content_layout.setContentsMargins(20, 20, 20, 20)

        # Add shadow elevation effects
        self._elevation = Shadow.ELEVATION_6
        self._elevation_enabled: bool = True

        if self._elevation_enabled:
            Effects.apply_shadow(self, self._elevation)

    def _create_header_container(self):
        """Create and configure the header container with nested layout structure.

        Initializes the header section of the card if it doesn't already exist.
        The header container uses a nested layout structure to accommodate both
        main headers with icons and optional subheaders with proper spacing.

        The structure created is:
        - Header Container (QWidget)
          - Header Main Layout (QVBoxLayout) - vertical stacking
            - Header Row Layout (QHBoxLayout) - horizontal for icon + text
            - Subheader space (when needed)

        Note:
            This method is called automatically when header-related methods are
            used. It's safe to call multiple times as it checks for existing
            containers before creating new ones.
        """
        if self._header_container:
            return

        # Create header container
        self._header_container = QWidget(self)
        self._header_container.setContentsMargins(25, 25, 25, 10)
        self._header_container.setAttribute(Qt.WA_StyledBackground, False)
        self._header_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # Accommodates header/sub-header
        self._header_main_layout = QVBoxLayout(self._header_container)
        self._header_main_layout.setContentsMargins(0, 0, 0, 0)
        self._header_main_layout.setSpacing(4)

        # Accommodates header icon
        self._header_row_layout = QHBoxLayout()
        self._header_row_layout.setContentsMargins(0, 0, 0, 0)
        self._header_row_layout.setSpacing(8)

        self._header_main_layout.addLayout(self._header_row_layout)

        # Add the header container to the main layout
        self._layout.insertWidget(0, self._header_container)

    @property
    def headerIcon(self) -> AppIcon | None:
        """Get direct access to the header's icon widget.

        Provides read-only access to the current header icon widget for
        external styling, event handling, or property inspection.

        Returns:
            AppIcon | None: The current header icon widget if one exists,
                otherwise None if no icon has been set.

        Note:
            This property returns the actual widget instance, allowing for
            direct manipulation of icon properties like size, color, or
            click handlers if needed.
        """
        return self._header_icon_widget

    def setHeader(self, text: str, icon: Optional[object] = None):
        """Set or update the card's main header text and optional icon.

        Creates or updates the primary header section of the card. The header
        appears at the top of the card and can include an icon for better
        visual identification and context.

        Args:
            text (str): The main header text to display. This text will be
                styled according to the "Header" QSS object name.
            icon (Optional[object]): An optional icon to display alongside
                the header text. Can be either:
                - A Name enum value (creates AppIcon automatically)
                - A QWidget instance (uses widget directly)
                - None (no icon displayed)

        Note:
            If a header already exists, this method updates the existing
            text and refreshes the widget styling. The header container
            is created automatically if it doesn't exist.
        """
        self._create_header_container()

        if not self._header_label:
            self._header_label = QLabel(text)
            self._header_label.setObjectName("Header")
            self._header_row_layout.addWidget(self._header_label, 0, Qt.AlignVCenter)
        else:
            self._header_label.setText(text)
            self._refresh_widget_style(self._header_label)

        if icon is not None:
            self.setHeaderIcon(icon)

    def setHeaderIcon(self, icon: object):
        """Set or replace the header's icon widget.

        Updates the icon displayed alongside the header text. If an icon
        already exists, it is properly removed and replaced with the new one.
        The icon is positioned to the left of the header text with appropriate
        vertical alignment.

        Args:
            icon (object): The icon to display. Supported types:
                - Name enum: Automatically converted to AppIcon widget
                - QWidget: Used directly as the icon widget

        Raises:
            ImportError: If Name enum is provided but AppIcon is not available.
            TypeError: If the icon parameter is not a supported type.

        Note:
            The icon widget is inserted at the beginning of the header row
            layout and is vertically centered with the header text.
        """
        self._create_header_container()

        if self._header_icon_widget:
            self._header_row_layout.removeWidget(self._header_icon_widget)
            self._header_icon_widget.deleteLater()

        if isinstance(icon, QWidget):
            self._header_icon_widget = icon
        elif Name and hasattr(icon, "spec"):
            if not AppIcon:
                raise ImportError("AppIcon widget not available.")
            self._header_icon_widget = AppIcon(icon)
        else:
            raise TypeError("Unsupported icon type. Pass a Name enum or QWidget.")

        self._header_row_layout.insertWidget(0, self._header_icon_widget, 0, Qt.AlignVCenter)

    def setSubHeader(self, text: str):
        """Set or update the subheader text."""
        self._create_header_container()

        if not self._subheader_label:
            self._subheader_label = QLabel(text)
            self._subheader_label.setObjectName("SubHeader")
            self._header_main_layout.addWidget(self._subheader_label)
        else:
            self._subheader_label.setText(text)

    def setSpacing(self, spacing: int):
        """Set the spacing for the card's content layout."""
        self._content_layout.setSpacing(spacing)

    def setHeaderMargins(self, margins: tuple[int, int, int, int]):
        """Set the content margins for the card's header."""
        self._header_container.setContentsMargins(*margins)

class ActionCard(Card):
    """A Card widget with button support."""
    def __init__(
        self,
        parent: QWidget | None = None,
        content_layout: str = "vbox",
        card_type: str = "Default",
    ):
        """Initialize the ActionCard widget.

        Args:
            parent: Optional parent widget.
            content_layout: Initial layout type: "vbox" (default), "hbox", or "grid".
            card_type: Card styling type for QSS (default: "Default").
        """
        super().__init__(parent, content_layout, card_type)

        self.setObjectName("ActionCard")

        self._footer_container: QWidget | None = None
        self._footer_layout:    QHBoxLayout | None = None
        self._footer_button:    Button | None = None

    def _create_footer_container(self):
        """Create the footer container for the card."""
        if self._footer_container:
            return

        # Create footer container
        self._footer_container = QWidget(self)
        self._footer_container.setObjectName("FooterContainer")

        # Create footer layout
        self._footer_layout = QHBoxLayout(self._footer_container)
        self._footer_layout.setContentsMargins(25, 25, 25, 25)
        self._footer_layout.setSpacing(0)

        # Add footer container to the main layout
        if self._layout:
            self._layout.addWidget(self._footer_container)

    @property
    def button(self) -> Button | None:
        """Direct access to the footer button widget."""
        return self._footer_button

    def addButton(self, text: str, type=None, icon=None, alignment=Qt.AlignCenter, callback=None):
        """Add a footer button to the card with alignment control.

        Args:
            text: Button text
            button_type: Button type from Type enum (optional)
            icon: Button icon from Name enum (optional)
            alignment: Button alignment (Qt.AlignLeft, Qt.AlignCenter, Qt.AlignRight)
            callback: Function to connect to button's clicked signal (optional)
        """
        self._create_footer_container()

        # Remove existing button if present
        if self._footer_button:
            self.removeButton()

        # Create button with default type if not specified
        if type is None:
            type = Type.PRIMARY

        self._footer_button = Button(text, type, icon)
        self._footer_button.setObjectName("ActionButton")
        self._button_alignment = alignment

        # Connect callback if provided
        if callback:
            self._footer_button.clicked.connect(callback)

        # Add to layout with alignment
        if self._footer_layout:
            self._footer_layout.addWidget(self._footer_button, 0, alignment)

    def removeButton(self):
        """Remove the footer button if it exists."""
        if self._footer_button and self._footer_layout:
            self._footer_layout.removeWidget(self._footer_button)
            self._footer_button.deleteLater()
            self._footer_button = None

