"""theme_loader/themes/dark_theme.py

Dark Theme definition used across the MealGenie application.
Supports dynamic QSS injection, theme-aware icons, and centralized style access.
"""

# ── Color Constants ─────────────────────────────────────────────────────────────
# Accents
ACCENT_PRIMARY             = "#03B79E"
ACCENT_PRIMARY_HOVER       = "#05CFAE"
ACCENT_PRIMARY_ACTIVE      = "#029E86"

ACCENT_SECONDARY           = "#3B575B"
ACCENT_SECONDARY_HOVER     = "#5A777A"
ACCENT_SECONDARY_ACTIVE    = "#2D4547"

# Surfaces / Backgrounds
SURFACE_MAIN               = "#3A4048"
SURFACE_RAISED             = "#2C313C"
BACKGROUND_WIDGET          = "#272C36"
BACKGROUND_INPUT           = "#B7BBC8"
BACKGROUND_PANEL           = "#525861"

# Borders
BORDER_DEFAULT             = "#1B1D23" 
BORDER_WIDGET              = "#555A60"
BORDER_ERROR               = "#FF4F4F"
DIVIDER                    = "#343b48"

# Text
TEXT_DEFAULT               = "#9DA1A5"
TEXT_STRONG                = "#E1E1E3"
TEXT_DISABLED              = "#6A6D72"
TEXT_INVERSE               = "#FFFFFF"

# Control States
STATE_HOVER                = "#424A52"
STATE_ACTIVE               = "#2E333D"
FOCUS_RING                 = "#1E90FF"

# Scrollbars
SCROLLBAR_TRACK            = "#424951"

# Semantic Status
STATUS_SUCCESS             = "#28A745"
STATUS_WARNING             = "#FFC107"
STATUS_ERROR               = "#DC3545"
STATUS_INFO                = "#17A2B8"


# ── Theme Dictionary ───────────────────────────────────────────────────────────
THEME = {
    "NAME": "Dark Theme",

    # ── Accent Colors ──────────────────────────────────────────────────────────
    "ACCENT": {
        "PRIMARY":          ACCENT_PRIMARY,
        "HOVER":            ACCENT_PRIMARY_HOVER,
        "ACTIVE":           ACCENT_PRIMARY_ACTIVE,
        "SECONDARY":        ACCENT_SECONDARY,
        "SECONDARY_HOVER":  ACCENT_SECONDARY_HOVER,
        "SECONDARY_ACTIVE": ACCENT_SECONDARY_ACTIVE,
    },

    # ── Backgrounds & Surfaces ──────────────────────────────────────────────────
    "BACKGROUND": {
        "DEFAULT":      SURFACE_MAIN,
        "RAISED":       SURFACE_RAISED,
        "WIDGET":       BACKGROUND_WIDGET,
        "PANEL":        BACKGROUND_PANEL,
        "INPUT":        BACKGROUND_INPUT,
    },

    # ── Text Colors ─────────────────────────────────────────────────────────────
    "TEXT": {
        "DEFAULT":      TEXT_DEFAULT,
        "STRONG":       TEXT_STRONG,
        "DISABLED":     TEXT_DISABLED,
        "INVERSE":      TEXT_INVERSE,
        "LINK":         ACCENT_PRIMARY,
    },

    # ── Borders & Dividers ──────────────────────────────────────────────────────
    "BORDER": {
        "DEFAULT":      BORDER_DEFAULT,
        "WIDGET":       BORDER_WIDGET,
        "ACTIVE":       ACCENT_PRIMARY,
        "ERROR":        BORDER_ERROR,
        "DIVIDER":      DIVIDER,
    },

    # ── Control States ──────────────────────────────────────────────────────────
    "STATE": {
        "PRIMARY": {
            "HOVER":        STATE_HOVER,
            "ACTIVE":       STATE_ACTIVE,
        },
        "SECONDARY": {
            "HOVER":        ACCENT_SECONDARY,
            "ACTIVE":       SURFACE_MAIN,
        },  
    },

    # ── Scrollbars ──────────────────────────────────────────────────────────────
    "SCROLLBAR": {
        "TRACK":        SCROLLBAR_TRACK,
        "HANDLE":       ACCENT_PRIMARY,
    },

    # ── Semantic Status Colors ──────────────────────────────────────────────────
    "STATUS": {
        "SUCCESS":      STATUS_SUCCESS,
        "WARNING":      STATUS_WARNING,
        "ERROR":        STATUS_ERROR,
        "INFO":         STATUS_INFO,
    },

    # ── Typography ──────────────────────────────────────────────────────────────
    
    "FONT": {
        "TITLE":        "Sakitu Baelah Clean",
        "HEADER":       "Montserrat",
        "BODY":         "Roboto",
        "UI":           "Open Sans",

        "SIZE": {
            "SMALL":    "12px",
            "NORMAL":   "16px",
            "LARGE":    "18px",
            "XLARGE":   "22px",
        },
    },

    # ── Spacing & Radius ────────────────────────────────────────────────────────
    "SPACING": {
        "UNIT":          "8px",
        "BORDER_RADIUS": "8px",
    },

    # ── Icon Colors ─────────────────────────────────────────────────────────────
    "ICON": {
        "DEFAULT":      TEXT_DEFAULT,
        "ACCENT":       ACCENT_PRIMARY,
        "HOVER":        ACCENT_SECONDARY,
        "DISABLED":     SURFACE_MAIN,
        "BOLD":         BACKGROUND_WIDGET,
        "INFO":         STATUS_INFO,
        "SUCCESS":      STATUS_SUCCESS,
        "WARNING":      STATUS_WARNING,
        "ERROR":        STATUS_ERROR,
    },

    # ── Dynamic Icon Styles ─────────────────────────────────────────────────────
    "ICON_STYLES": {
        "NAV": {
            "DEFAULT":  TEXT_DEFAULT,
            "HOVER":    ACCENT_PRIMARY,
            "CHECKED":  ACCENT_PRIMARY,
            "DISABLED": TEXT_DEFAULT,
        },
        "TOOLBUTTON": {
            "DEFAULT":  TEXT_DEFAULT,
            "HOVER":    ACCENT_PRIMARY,
            "CHECKED":  ACCENT_SECONDARY,
            "DISABLED": TEXT_DISABLED,
        },
    },
}
