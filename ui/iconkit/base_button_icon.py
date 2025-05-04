"""ui/iconkit/icon_widgets/base_button_icon.py   ← I renamed file for clarity
Mixin base for QPushButton / QToolButton icons with themed SVG states.
"""

# ── Imports ───────────────────────────────────────────────────────────────
from PySide6.QtCore import QSize

from core.controllers.icon_controller import IconController
from ui.iconkit import IconFactory
from ui.iconkit.effects import ApplyHoverEffects

# ── Class ─────────────────────────────────────────────────────────────────
class BaseButtonIcon():
    """
    Call `_init_icon_button(name, size)` inside your subclass __init__.
    Handles theme registration & live recolouring.
    """

    # ── Public Methods ──────────────────────────────────────────────────────────────
    def _init_button_icon(
            self, 
            file_name: str, 
            size: QSize, 
            variant: str = "default"
        ) -> None:
        """
        Initialize the icon button with a file name, size, and variant.
        
        Args:
            file_name (str): The name of the SVG file.
            size (QSize): The size of the icon.
            variant (str, optional): The variant of the icon. Defaults to "default".
        """
        self.file_name = file_name         
        self.size      = size    
        self.variant   = variant 

        self.setCheckable(True)  
        IconController().register(self) # auto-tracks this widget
        self.refresh_theme(IconController().palette)

    # called by IconController when theme flips
    def refresh_theme(self, palette: dict) -> None:
        """
        Update the icon colors based on the theme's ICON_STYLES.

        This method supports complex styles like:
        {
            "ICON_STYLES": {
                "nav": {
                    "default": "NAV_ICON_DEFAULT",
                    "hover":   "NAV_ICON_HOVER",
                    "checked": "NAV_ICON_CHECKED"
                }
            }
        }
        """
        style_map = palette.get("ICON_STYLES", {})
        style = style_map.get(self.variant, {})  # Could be dict or string fallback

        # Determine palette keys
        if isinstance(style, dict):
            default_key = style.get("default", "ICON_COLOR")
            hover_key   = style.get("hover", "ICON_COLOR_HOVER")
            checked_key = style.get("checked", "ICON_COLOR_CHECKED")
        else:
            # fallback: single-color variant (legacy)
            default_key = style
            hover_key   = "ICON_COLOR_HOVER"
            checked_key = "ICON_COLOR_CHECKED"

        # Get color values
        default_color = palette.get(default_key, "#FFFFFF")
        hover_color   = palette.get(hover_key, "#CCCCCC")
        checked_color = palette.get(checked_key, "#999999")

        # Apply icons
        default_icon, hover_icon, checked_icon = IconFactory.make_icons(
            file_name=self.file_name,
            size=self.size,
            default_color=default_color,
            hover_color=hover_color,
            checked_color=checked_color
        )

        ApplyHoverEffects.apply(self, default_icon, hover_icon, checked_icon)
        self.setIcon(default_icon)
        self._hover_icon = hover_icon
        self._checked_icon = checked_icon
        self.setIconSize(self.size)
