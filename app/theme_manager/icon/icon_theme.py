"""app/style_manager/themes/dark_theme.py

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
SURFACE_RAISED             = "#1b1d23"
BACKGROUND_WIDGET          = "#272C36"
BACKGROUND_INPUT           = "#B7BBC8"
BACKGROUND_PANEL           = "#525861"

# Borders
BORDER_DEFAULT             = "#231B1B"
BORDER_WINNDOW             = "#2F2F2F"
BORDER_WIDGET              = "#555A60"
BORDER_ERROR               = "#FF4F4F"
DIVIDER                    = "#343b48"

# Text
TEXT_DEFAULT               = "#9DA1A5"
TEXT_CONTRAST              = "#E1E1E3"
TEXT_INVERSE               = "#2F2F2F"
TEXT_DISABLED              = "#6A6D72"
TEXT_ERROR                 = "#973B3B"
TEXT_SUCCESS               = "#3D7D4C"


# Control States
STATE_HOVER                = "#424A52"
STATE_ACTIVE               = "#2E333D"
IMPORTANT                  = "#1E90FF"

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
    "WINDOW_RADIUS": "10px",
    "CORNER_WIDGET_RADIUS": "9px",

    # ── Backgrounds & Surfaces ──────────────────────────────────────────────────
    "BACKGROUND": {
        "DEFAULT":      SURFACE_MAIN,
        "RAISED":       SURFACE_RAISED,
        "WIDGET":       BACKGROUND_WIDGET,
        "PANEL":        BACKGROUND_PANEL,
        "INPUT":        BACKGROUND_INPUT,
    },

    # ── Control States ──────────────────────────────────────────────────────────
    "STATE": {
        "PRIMARY": {
            "HOVER":     STATE_HOVER,
            "ACTIVE":    STATE_ACTIVE,
        },
        "SECONDARY": {
            "HOVER":     ACCENT_SECONDARY,
            "ACTIVE":    SURFACE_MAIN,
        },
        "CLOSE":         TEXT_ERROR,
    },

    # ── Typography ──────────────────────────────────────────────────────────────
    "FONT": {
        "FAMILY": {
            "DEFAULT":  "Roboto",
            "TITLE":    "Sakitu Baelah Clean",
            "HEADER":   "Montserrat",
            "BODY":     "Roboto",
            "UI":       "Open Sans",
        },

        "SIZE": {
            "XSMALL":   "14px",
            "SMALL":    "16px",
            "DEFAULT":  "20px",
            "LARGE":    "24px",
            "XLARGE":   "26px",
        },

        "COLOR": {
            "DEFAULT":  TEXT_DEFAULT,
            "CONTRAST": TEXT_CONTRAST,
            "INVERSE":  TEXT_INVERSE,
            "DISABLED": TEXT_DISABLED,
            "ERROR":    TEXT_ERROR,
            "SUCCESS":  TEXT_SUCCESS,
        }
    },

    # ── Accent Colors ──────────────────────────────────────────────────────────
    "ACCENT": {
        "PRIMARY":          ACCENT_PRIMARY,
        "HOVER":            ACCENT_PRIMARY_HOVER,
        "ACTIVE":           ACCENT_PRIMARY_ACTIVE,
        "SECONDARY":        ACCENT_SECONDARY,
        "SECONDARY_HOVER":  ACCENT_SECONDARY_HOVER,
        "SECONDARY_ACTIVE": ACCENT_SECONDARY_ACTIVE,
    },

    # ── Borders & Dividers ──────────────────────────────────────────────────────
    "BORDER": {
        "DEFAULT":      BORDER_DEFAULT,
        "WINDOW":       BORDER_WINNDOW,
        "WIDGET":       BORDER_WIDGET,
        "ACTIVE":       ACCENT_PRIMARY,
        "ERROR":        BORDER_ERROR,
        "DIVIDER":      DIVIDER,
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
            "CHECKED":  ACCENT_PRIMARY,
            "DISABLED": TEXT_DISABLED,
        },
        "TITLEBAR": {
            "DEFAULT":  TEXT_DEFAULT,
            "HOVER":    TEXT_CONTRAST,
            "CHECKED":  ACCENT_SECONDARY,
            "DISABLED": TEXT_DISABLED,
        },
    },
}
