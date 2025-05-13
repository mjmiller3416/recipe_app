"""dark_theme.py

Dark Theme definition used across the MealGenie application.
Supports dynamic QSS injection, theme-aware icons, and centralized style access.
"""

THEME = {
    # ── Meta ───────────────────────────────────────────────────────────────
    "NAME": "Dark Theme",

    # ── Accent Colors (Brand/Highlighting) ─────────────────────────────────
    "ACCENT": {
        "DEFAULT":    "#03B79E",  # primary accent color
        "SECONDARY":  "#6AD7CA",
        "HIGHLIGHT":  "#3B575B",
    },

    # ── Surface / Backgrounds ──────────────────────────────────────────────
    "BACKGROUND": {
        "DEFAULT":  "#1B1D23",
        "MUTED":    "#2C313C",
        "RAISED":   "#3A4048",
        "WIDGET":   "#272C36",
        "INPUT":    "#525861",
    },

    # ── Text ───────────────────────────────────────────────────────────────
    "TEXT": {
        "DEFAULT":   "#9DA1A5",
        "STRONG":    "#E1E1E3",
        "DISABLED":  "#6A6D72",
    },

    # ── Borders ────────────────────────────────────────────────────────────
    "BORDER": {
        "DEFAULT": "#424951",
        "ACTIVE":  "#6AD7CA",
        "ERROR":   "#FF4F4F",
    },

    # ── Control States ─────────────────────────────────────────────────────
    "CONTROL": {
        "DEFAULT": "#949AA7",
        "HOVER":   "#6AD7CA",
        "CHECKED": "#3A4048",
    },

    # ── Scrollbars ─────────────────────────────────────────────────────────
    "SCROLLBAR": {
        "TRACK":  "#424951",
        "HANDLE": "#03B79E",
    },

    # ── Typography ─────────────────────────────────────────────────────────
    "FONTS": {
        "TITLE": "Sakitu Baelah Clean",
        "HEADER":  "Montserrat",
        "BODY":    "Roboto",
        "UI":      "Open Sans",

        "SIZE": {
            "SMALL":  "12px",
            "NORMAL": "16px",
            "LARGE":  "18px",
            "XLARGE": "22px",
        },
    },

    # ── Spacing & Radius ───────────────────────────────────────────────────
    "SPACING": {
        "UNIT":          "8px",
        "BORDER_RADIUS": "8px",
    },

    # ── Icon Colors ────────────────────────────────────────────────────────
    "ICON": {
        "DEFAULT":  "#949AA7",
        "ACCENT":   "#03B79E",
        "HOVER":    "#6AD7CA",
        "disabled": "#5A5E66",

        # ── Status Indicators ─────────────────────────────────────────────
        "INFO":     "#4FD1C5",
        "SUCCESS":  "#6ACB81",
        "WARNING":  "#FBBF24",
        "ERROR":    "#FF4F4F",
    },

    # ── Themed Icon Variants ───────────────────────────────────────────────
    "ICON_STYLES": {
        "NAV": {
            "DEFAULT":  "#949AA7",
            "HOVER":    "#3A4048",
            "CHECKED":  "#006eff",
            "DISABLED": "#5A5E66",
        },
        "TITLEBAR": {
            "DEFAULT":  "#949AA7",
            "HOVER":    "#6AD7CA",
            "CHECKED":  "#6AD7CA",
            "DISABLED": "#5A5E66",
        },
        "RECIPE_CARD": {
            "DEFAULT":  "#6AD7CA",
            "HOVER":    "#3B575B",
            "CHECKED":  "#6AD7CA",
            "DISABLED": "#5A5E66",
        },
    },
}
