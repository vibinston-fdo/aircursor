"""
AirCursor Pro — Config Manager
Persists runtime configuration to a JSON file.
Merges JSON values over config.py defaults so the app always has
safe fallback values even if the JSON file is missing or corrupt.
"""
import json
import os
import threading
from src.core import config
from src.core.logger import get_logger

log = get_logger("ConfigManager")

# Keys that can be saved/loaded (with their default values)
_DEFAULTS: dict = {
    "TRACK_LEFT":               config.TRACK_LEFT,
    "TRACK_RIGHT":              config.TRACK_RIGHT,
    "TRACK_TOP":                config.TRACK_TOP,
    "TRACK_BOTTOM":             config.TRACK_BOTTOM,
    "SMOOTHING_MIN_CUTOFF":     config.SMOOTHING_MIN_CUTOFF,
    "SMOOTHING_BETA":           config.SMOOTHING_BETA,
    "DEADZONE":                 config.DEADZONE,
    "PINCH_LEFT_START":         config.PINCH_LEFT_START,
    "PINCH_LEFT_RELEASE":       config.PINCH_LEFT_RELEASE,
    "PINCH_RIGHT_START":        config.PINCH_RIGHT_START,
    "PINCH_RIGHT_RELEASE":      config.PINCH_RIGHT_RELEASE,
    "PINCH_CONFIRMATION_TIME":  config.PINCH_CONFIRMATION_TIME,
    "DRAG_HOLD_TIME":           config.DRAG_HOLD_TIME,
    "CLICK_COOLDOWN":           config.CLICK_COOLDOWN,
    "DOUBLE_CLICK_WINDOW":      config.DOUBLE_CLICK_WINDOW,
    "GESTURE_COOLDOWN_TIME":    config.GESTURE_COOLDOWN_TIME,
    "SCROLL_SENSITIVITY":       config.SCROLL_SENSITIVITY,
    "SCROLL_DEADZONE":          config.SCROLL_DEADZONE,
    "SCROLL_CONFIRMATION_FRAMES": config.SCROLL_CONFIRMATION_FRAMES,
    "DETECTION_CONFIDENCE":     config.DETECTION_CONFIDENCE,
    "TRACKING_CONFIDENCE":      config.TRACKING_CONFIDENCE,
    "PERF_MODE":                config.PERF_MODE,
    "CALIBRATION_VALID":        False,
    "CALIBRATION_DATE":         "",
}

# Value bounds for validation
_BOUNDS: dict = {
    "TRACK_LEFT":   (0.0, 0.49),   "TRACK_RIGHT":  (0.51, 1.0),
    "TRACK_TOP":    (0.0, 0.49),   "TRACK_BOTTOM": (0.51, 1.0),
    "SMOOTHING_MIN_CUTOFF": (0.05, 10.0),
    "SMOOTHING_BETA":       (0.0,  50.0),
    "DEADZONE":             (0.0,  20.0),
    "PINCH_LEFT_START":     (0.01, 0.20),
    "PINCH_LEFT_RELEASE":   (0.01, 0.25),
    "PINCH_RIGHT_START":    (0.01, 0.20),
    "PINCH_RIGHT_RELEASE":  (0.01, 0.25),
    "PINCH_CONFIRMATION_TIME": (0.02, 0.5),
    "DRAG_HOLD_TIME":       (0.1,  2.0),
    "CLICK_COOLDOWN":       (0.1,  1.0),
    "DOUBLE_CLICK_WINDOW":  (0.2,  1.5),
    "GESTURE_COOLDOWN_TIME":(0.05, 1.0),
    "SCROLL_SENSITIVITY":   (0.5,  20.0),
    "SCROLL_DEADZONE":      (0.001,0.1),
    "SCROLL_CONFIRMATION_FRAMES": (2, 20),
    "DETECTION_CONFIDENCE": (0.3,  1.0),
    "TRACKING_CONFIDENCE":  (0.3,  1.0),
}


class ConfigManager:
    """Thread-safe, singleton config manager."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._data: dict = dict(_DEFAULTS)
                cls._instance._file = config.CONFIG_FILE
                cls._instance._load()
            return cls._instance

    # ── Public API ─────────────────────────────────────────────

    def get(self, key: str, fallback=None):
        return self._data.get(key, fallback if fallback is not None else _DEFAULTS.get(key))

    def set(self, key: str, value) -> bool:
        """Validate and store a value. Returns True if accepted."""
        if key not in _DEFAULTS:
            log.warning(f"Unknown config key: {key}")
            return False
        if key in _BOUNDS:
            lo, hi = _BOUNDS[key]
            if isinstance(value, (int, float)):
                if not (lo <= value <= hi):
                    log.warning(f"Config {key}={value} out of bounds [{lo}, {hi}]")
                    return False
        self._data[key] = value
        # Propagate to config module so live code sees the new value
        if hasattr(config, key):
            setattr(config, key, value)
        return True

    def save(self):
        """Write current config to JSON file."""
        try:
            with open(self._file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            log.info(f"Config saved to {self._file}")
        except OSError as e:
            log.error(f"Failed to save config: {e}")

    def reset_to_defaults(self):
        """Restore all values to code defaults."""
        self._data = dict(_DEFAULTS)
        for k, v in _DEFAULTS.items():
            if hasattr(config, k):
                setattr(config, k, v)
        log.info("Config reset to defaults")

    def as_dict(self) -> dict:
        return dict(self._data)

    # ── Private ────────────────────────────────────────────────

    def _load(self):
        if not os.path.exists(self._file):
            log.info("No config file found — using defaults")
            return
        try:
            with open(self._file, encoding="utf-8") as f:
                saved: dict = json.load(f)
            for k, v in saved.items():
                if k in _DEFAULTS:
                    self.set(k, v)   # validates bounds
            log.info(f"Config loaded from {self._file}")
        except (json.JSONDecodeError, OSError) as e:
            log.error(f"Could not load config ({e}) — using defaults")
