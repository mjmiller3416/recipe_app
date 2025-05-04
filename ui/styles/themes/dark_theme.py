THEME = {
    # ── Core Brand ─────────────────────────────────────────────────────────────────────────────────────────
    "PRIMARY_COLOR":      "#03B79E",            # Teal accent color
    "SECONDARY_COLOR":    "#3B575B",            # Soft steel blue / hover
    "ACCENT_COLOR":       "#03B79E",            # Same as primary

    # ── Backgrounds ────────────────────────────────────────────────────────────────────────────────────────
    "BACKGROUND_DARK":    "#1B1D23",            # Primary background (window, titlebar)
    "BACKGROUND_MEDIUM":  "#2C313C",            # Panels / wrappers
    "BACKGROUND_LIGHT":   "#3A4048",            # Cards / secondary panels
    "WIDGET_BG":          "#272C36",            # Inputs / sidebar

    # ── Text ───────────────────────────────────────────────────────────────────────────────────────────────
    "TEXT_PRIMARY":       "#E1E1E3",            # Main white text
    "TEXT_SECONDARY":     "#9DA1A5",            # Subtext, descriptions

    # ── Borders / Highlights ───────────────────────────────────────────────────────────────────────────────
    "BORDER_COLOR":       "#424951",            # Field borders, separators
    "HIGHLIGHT_COLOR":    "#6AD7CA",            # Username, labels
    "ERROR_BORDER":       "#FF4F4F",            # Error border for inputs
    
    # ── Inputs / Scrollbars ────────────────────────────────────────────────────────────────────────────────
    "INPUT_BG":           "#525861",            # QLineEdit, QComboBox, etc.
    "SCROLLBAR_BG":       "#424951",            # Scrollbar track
    "SCROLLBAR_HANDLE":   "#03B79E",            # Scrollbar grabber
    
    # ── Icons ──────────────────────────────────────────────────────────────────────────────────────────────
    "ICON_COLOR":         "#949AA7",            # Default icon color
    "LOGO_COLOR":         "#949AA7",            # Logo color
    "ICON_COLOR_HOVER":   "#6AD7CA",            # Icon hover color
    "ICON_COLOR_CHECKED": "#6AD7CA",            # Icon checked color
    "NAV_ICON_DEFAULT":   "#949AA7",            # Default nav icon color
    "NAV_ICON_HOVER":     "#6AD7CA",            # Nav icon hover color
    "NAV_ICON_CHECKED":   "#6AD7CA",            # Nav icon checked color
    "SUCCESS_COLOR":      "#5CDE42",            # Success green
    "ERROR_COLOR":        "#FF4D4D",            # Error red
    "WARNING_COLOR":      "#FFCC00",            # Warning yellow
    "INFO_COLOR":         "#6AD7CA",            # Info teal
    
    # ── Spacing ────────────────────────────────────────────────────────────────────────────────────────────
    "BORDER_RADIUS":      "8px",                  # Rounded corners for buttons, inputs, etc.
    "SPACING_UNIT":       "8px",                  # Base spacing unit for margins, paddings, etc.

    # ── Typography ─────────────────────────────────────────────────────────────────────────────────────────
    "FONT_DISPLAY":       "Sakitu Baelah Clean",  # Big headings / titles
    "FONT_HEADER":        "Montserrat",           # Headers, titles, etc.
    "FONT_BODY":          "Roboto",               # Body text, paragraphs, etc.
    "FONT_UI":            "Open Sans",            # Buttons, inputs, etc.
    "FONT_SIZE_SMALL":    "12px",                 # Small text (e.g. footnotes, captions)
    "FONT_SIZE_NORMAL":   "14px",                 # Normal text (e.g. body, labels)
    "FONT_SIZE_LARGE":    "18px",                 # Large text (e.g. headings, titles)

    # ── Icons Variants ─────────────────────────────────────────────────────────────────────────────────────
    "ICON_STYLES": {
        "default": {
            "default": "ICON_COLOR",
            "hover": "ICON_COLOR_HOVER",
            "checked": "ICON_COLOR_CHECKED"
        },
        "nav": {
            "default": "NAV_ICON_DEFAULT",
            "hover": "NAV_ICON_HOVER",
            "checked": "NAV_ICON_CHECKED"
        },
        "titlebar": {
            "default": "TITLEBAR_ICON_DEFAULT",
            "hover": "TITLEBAR_ICON_HOVER",
            "checked": "TITLEBAR_ICON_CHECKED"
        },
    }
}
