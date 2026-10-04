"""
AirCursor Pro — Central Configuration
All tuneable values live here. Runtime overrides managed by ConfigManager.
"""
import os

# ── App identity ───────────────────────────────────────────────
APP_TITLE    = "AirCursor Pro"
APP_SUBTITLE = "Vision-Based Touchless Human-Computer Interaction"
APP_VERSION  = "4.0.0"

# Persistent config stored next to the project root
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_FILE = os.path.join(_ROOT, "aircursor_config.json")

# ── Camera ─────────────────────────────────────────────────────
CAMERA_ID    = 0
FRAME_WIDTH  = 640
FRAME_HEIGHT = 480
FPS_SMOOTHING = 0.9

# MediaPipe confidence
DETECTION_CONFIDENCE = 0.70
TRACKING_CONFIDENCE  = 0.70
MAX_HANDS            = 1

# ── Tracking Zone (normalised camera coords) ───────────────────
# These are overwritten at runtime from ConfigManager / calibration.
TRACK_LEFT   = 0.15
TRACK_RIGHT  = 0.85
TRACK_TOP    = 0.15
TRACK_BOTTOM = 0.75

# ── One-Euro Filter ────────────────────────────────────────────
SMOOTHING_MIN_CUTOFF = 0.5
SMOOTHING_BETA       = 5.0
DEADZONE             = 2.0           # pixels

# ── Pinch thresholds (normalised by hand size) ─────────────────
PINCH_LEFT_START    = 0.055
PINCH_LEFT_RELEASE  = 0.080
PINCH_RIGHT_START   = 0.055
PINCH_RIGHT_RELEASE = 0.080

PINCH_CONFIRMATION_TIME = 0.08      # s – prevents single-frame triggers
DRAG_HOLD_TIME          = 0.45      # s – short < this → click; longer → drag
CLICK_COOLDOWN          = 0.35      # s – min between left clicks
DOUBLE_CLICK_WINDOW     = 0.55      # s – window to detect second pinch
GESTURE_COOLDOWN_TIME   = 0.30      # s – time in COOLDOWN state

# ── Scroll ─────────────────────────────────────────────────────
SCROLL_CONFIRMATION_FRAMES = 5      # frames of peace-sign before entering scroll
SCROLL_SENSITIVITY         = 5.0    # scroll clicks per unit of Y delta
SCROLL_DEADZONE            = 0.015  # normalised Y units
SCROLL_COOLDOWN_S          = 0.07   # s – min between scroll events

# ── Performance mode ───────────────────────────────────────────
PERF_MODE = "BALANCED"              # "QUALITY" | "BALANCED" | "PERFORMANCE"

# ── Safety ─────────────────────────────────────────────────────
EMERGENCY_KEY = "esc"
