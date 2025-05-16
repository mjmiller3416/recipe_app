"""dark_theme.py

Dark Theme definition used across the MealGenie application.
Supports dynamic QSS injection, theme-aware icons, and centralized style access.
"""

# ── Constants ───────────────────────────────────────────────────────────────────
PRIMARY_ACCENT = "#03B79E"
SECONDARY_ACCENT = "#3B575B"

SURFACE_LIGHT = "#3A4048"
SURFACE_DEFAULT = "#2C313C"
SURFACE_DARK = "#272C36"

BORDER = "#1B1D23"

TEXT_DEFAULT = "#9DA1A5"
TEXT_STRONG = "#E1E1E3"
TEXT_DISABLED = "#6A6D72"

THEME = {
    # ── Meta ───────────────────────────────────────────────────────────────
    "NAME": "Dark Theme",

    # ── Accent Colors (Brand/Highlighting) ─────────────────────────────────
    "ACCENT": {
        "DEFAULT":   PRIMARY_ACCENT,  
        "SECONDARY": SECONDARY_ACCENT,
        "HIGHLIGHT": SURFACE_DARK,
    },

    # ── Surface / Backgrounds ──────────────────────────────────────────────
    "BACKGROUND": {
        "DEFAULT":  SURFACE_DEFAULT,
        "MUTED":    "#2C313C",
        "RAISED":   "#3A4048",
        "WIDGET":   "#272C36",
        "INPUT":    "#525861",
    },

    # ── Text ───────────────────────────────────────────────────────────────
    "TEXT": {
        "DEFAULT":   TEXT_DEFAULT,
        "STRONG":    TEXT_STRONG,
        "DISABLED":  TEXT_DISABLED,
    },

    # ── Borders ────────────────────────────────────────────────────────────
    "BORDER": {
        "DEFAULT": BORDER,
        "ACTIVE":  PRIMARY_ACCENT,
        "ERROR":   "#FF4F4F",
    },

    # ── Control States ─────────────────────────────────────────────────────
    "CONTROL": {
        "DEFAULT": "#949AA7",
        "HOVER":   SECONDARY_ACCENT,
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
        "DEFAULT":  TEXT_DEFAULT,
        "ACCENT":   PRIMARY_ACCENT,
        "HOVER":    SECONDARY_ACCENT,
        "DISABLED": SURFACE_LIGHT,

        # ── Status Indicators ─────────────────────────────────────────────
        "INFO":     "#4FD1C5",
        "SUCCESS":  "#6ACB81",
        "WARNING":  "#FBBF24",
        "ERROR":    "#FF4F4F",
    },

    # ── Themed Icon Variants ───────────────────────────────────────────────
    "ICON_STYLES": {
        "NAV": {
            "DEFAULT":  TEXT_DEFAULT,
            "HOVER":    TEXT_DEFAULT,
            "CHECKED":  PRIMARY_ACCENT,
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
