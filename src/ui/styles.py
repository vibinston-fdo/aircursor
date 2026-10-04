"""
AirCursor Pro — UI Styles & Theme Constants
"""

APP_STYLE = (
    "QMainWindow, QWidget { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI'; }"
    "QLabel { color: #c9d1d9; }"
)

VIDEO_STYLE = (
    "QLabel {"
    "  background-color: #0d1117;"
    "  color: #8b949e;"
    "  border-radius: 12px;"
    "  border: 2px solid #30363d;"
    "}"
)

PANEL_STYLE = (
    "QFrame {"
    "  background-color: #161b22;"
    "  border-radius: 12px;"
    "  border: 1px solid #30363d;"
    "}"
    "QLabel { color: #c9d1d9; background: transparent; border: none; }"
)

BTN_OFF = (
    "QPushButton {"
    "  background-color: #21262d;"
    "  color: #8b949e;"
    "  border: 1px solid #30363d;"
    "  border-radius: 6px;"
    "  padding: 8px 12px;"
    "  font-weight: bold;"
    "  font-size: 12px;"
    "}"
    "QPushButton:hover { background-color: #30363d; color: #c9d1d9; }"
)

BTN_ON = (
    "QPushButton {"
    "  background-color: #238636;"
    "  color: #ffffff;"
    "  border: 1px solid #2ea043;"
    "  border-radius: 6px;"
    "  padding: 8px 12px;"
    "  font-weight: bold;"
    "  font-size: 12px;"
    "}"
    "QPushButton:hover { background-color: #2ea043; }"
)

BTN_DANGER = (
    "QPushButton {"
    "  background-color: #da3633;"
    "  color: #ffffff;"
    "  border: 1px solid #b3261e;"
    "  border-radius: 6px;"
    "  padding: 8px 12px;"
    "  font-weight: bold;"
    "  font-size: 12px;"
    "}"
    "QPushButton:hover { background-color: #b3261e; }"
)

NAV_BTN = (
    "QPushButton {"
    "  background-color: transparent;"
    "  color: #8b949e;"
    "  border: none;"
    "  padding: 10px 16px;"
    "  font-size: 14px;"
    "  font-weight: bold;"
    "  text-align: left;"
    "  border-radius: 6px;"
    "}"
    "QPushButton:hover { background-color: #21262d; color: #c9d1d9; }"
    "QPushButton:checked { background-color: #1f6feb; color: #ffffff; }"
)

BANNER_BASE = (
    "QLabel {"
    "  border-radius: 8px;"
    "  padding: 10px 18px;"
    "  font-weight: bold;"
    "  font-size: 15px;"
    "}"
)

# Colors
COLOR_IDLE = "#8b949e"
COLOR_ACTIVE = "#56d364"
COLOR_WARN = "#e3b341"
COLOR_ERROR = "#f78166"
COLOR_HIGHLIGHT = "#58a6ff"

GESTURE_COLORS = {
    "LEFT_CLICK":   ("#1f6feb", "#58a6ff"),
    "DOUBLE_CLICK": ("#9a38a0", "#d2a8ff"),
    "RIGHT_CLICK":  ("#b08800", "#e3b341"),
    "DRAG_START":   ("#1b4b2f", "#56d364"),
    "DRAG_END":     ("#1b4b2f", "#56d364"),
    "SCROLL_UP":    ("#21262d", "#c9d1d9"),
    "SCROLL_DOWN":  ("#21262d", "#c9d1d9"),
    "NONE":         ("#21262d", "#8b949e"),
}

GESTURE_LABELS = {
    "LEFT_CLICK":   "✓  LEFT CLICK",
    "DOUBLE_CLICK": "✓✓ DOUBLE CLICK",
    "RIGHT_CLICK":  "✓  RIGHT CLICK",
    "DRAG_START":   "●  DRAG START",
    "DRAG_END":     "○  DRAG END",
    "SCROLL_UP":    "↑  SCROLL UP",
    "SCROLL_DOWN":  "↓  SCROLL DOWN",
}
