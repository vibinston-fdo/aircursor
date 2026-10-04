"""
AirCursor Pro — Centralised Safety Controller
ONE place that handles every emergency stop scenario.
All mouse actions must flow through this or through components
that this controller can instantly override.
"""
import threading
from src.core.logger import get_logger

log = get_logger("Safety")


class SafetyController:
    """
    Central safety arbiter.
    Components register themselves; emergency_stop() disables them all.
    Thread-safe — can be called from pynput, vision thread, or UI thread.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                obj = super().__new__(cls)
                obj._cursor_ctrl = None
                obj._gesture_eng = None
                obj._stopped = False
                cls._instance = obj
            return cls._instance

    # ── Registration ───────────────────────────────────────────

    def register_cursor(self, ctrl):
        self._cursor_ctrl = ctrl

    def register_gesture(self, eng):
        self._gesture_eng = eng

    # ── Emergency stop ─────────────────────────────────────────

    def emergency_stop(self, reason: str = "ESC"):
        """
        Immediately:
        - Release all mouse buttons
        - Disable cursor control
        - Reset gesture state
        - Clear cooldowns
        Thread-safe.
        """
        log.warning(f"EMERGENCY STOP triggered — reason: {reason}")

        if self._gesture_eng is not None:
            try:
                self._gesture_eng.emergency_stop()
            except Exception as e:
                log.error(f"Gesture stop error: {e}")

        if self._cursor_ctrl is not None:
            try:
                self._cursor_ctrl.hard_stop()
            except Exception as e:
                log.error(f"Cursor stop error: {e}")

    # ── Session reset (softer than emergency) ──────────────────

    def reset_session(self):
        """
        Soft reset:
        - Stop cursor movement
        - Release any held buttons
        - Reset gesture state
        - Keep camera and tracking running
        """
        log.info("Session reset")
        if self._gesture_eng is not None:
            self._gesture_eng.emergency_stop()
        if self._cursor_ctrl is not None:
            self._cursor_ctrl.hard_stop()
