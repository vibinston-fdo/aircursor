"""
Mouse / Cursor Controller — AirCursor Pro Phase 4
==================================================
- Maps index-fingertip coords to screen coords
- Applies One-Euro smoothing + dead-zone
- Executes OS mouse actions via pynput
- Tracks button state (never leaves buttons stuck)
- Routes ESC through SafetyController
"""

import time
import math
import ctypes

from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Listener as KeyListener, Key

from src.engine.one_euro_filter import OneEuroFilter
from src.engine.gesture_engine import GestureEvent
from src.core import config
from src.core.logger import get_logger

log = get_logger("Cursor")


class CursorController:
    def __init__(self):
        self.mouse = MouseController()

        # Windows DPI-aware screen size
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.screen_w = user32.GetSystemMetrics(0)
        self.screen_h = user32.GetSystemMetrics(1)
        log.info(f"Screen: {self.screen_w}x{self.screen_h}")

        # State
        self.enabled          = False
        self._btn_left_down   = False
        self._btn_right_down  = False

        # Smoothing filters
        self._fx: OneEuroFilter | None = None
        self._fy: OneEuroFilter | None = None

        # Telemetry
        self.last_update_time  = time.time()
        self.update_rate       = 0.0
        self.proc_time_ms      = 0.0
        self.last_screen_pos: tuple[int, int] | None = None

        # ESC via pynput — routes to SafetyController (set after creation)
        self._safety = None
        self._kb = KeyListener(on_press=self._on_key)
        self._kb.daemon = True
        self._kb.start()

    def set_safety(self, safety):
        self._safety = safety

    # ── Emergency / hard stop ─────────────────────────────────

    def hard_stop(self):
        """Release everything and disable. Called by SafetyController."""
        self._release_all()
        self.enabled = False
        self._reset_filters()
        log.info("Cursor hard stop executed")

    def on_hand_lost(self):
        """Pause cursor without moving to 0,0. Reset filter."""
        self._reset_filters()

    # ── Main per-frame entry ──────────────────────────────────

    def process(self, index_x: float, index_y: float,
                gesture_event: GestureEvent,
                is_dragging: bool,
                scroll_amount: int = 0) -> tuple[int | None, int | None]:

        if not self.enabled:
            return None, None

        t0  = time.perf_counter()
        now = time.time()

        # 1. Map tracking zone → screen
        tx = (index_x - config.TRACK_LEFT)  / max(config.TRACK_RIGHT  - config.TRACK_LEFT,  1e-6)
        ty = (index_y - config.TRACK_TOP)   / max(config.TRACK_BOTTOM - config.TRACK_TOP,   1e-6)
        tx = max(0.0, min(1.0, tx))
        ty = max(0.0, min(1.0, ty))

        raw_x = tx * self.screen_w
        raw_y = ty * self.screen_h

        # 2. Smooth
        if self._fx is None:
            self._init_filters(now, raw_x, raw_y)
            sx, sy = raw_x, raw_y
        else:
            sx = self._fx(now, raw_x)
            sy = self._fy(now, raw_y)

        sx_i, sy_i = int(sx), int(sy)

        # 3. Dead-zone — only move cursor if delta > threshold
        cur = self.mouse.position
        if math.hypot(sx_i - cur[0], sy_i - cur[1]) > config.DEADZONE:
            self.mouse.position = (sx_i, sy_i)

        self.last_screen_pos = (sx_i, sy_i)

        # 4. Gesture events
        self._apply_event(gesture_event, scroll_amount)

        # 5. Drag safety sync
        if is_dragging and not self._btn_left_down:
            self._press_left()
        elif not is_dragging and self._btn_left_down:
            self._release_left()

        # 6. Telemetry
        self.proc_time_ms = (time.perf_counter() - t0) * 1000.0
        diff = now - self.last_update_time
        if diff > 0:
            self.update_rate = self.update_rate * 0.9 + (1.0 / diff) * 0.1
        self.last_update_time = now

        return sx_i, sy_i

    # ── Gesture dispatcher ────────────────────────────────────

    def _apply_event(self, event: GestureEvent, scroll_amount: int):
        if event == GestureEvent.LEFT_CLICK:
            log.info("LEFT CLICK")
            self._click_left()
        elif event == GestureEvent.DOUBLE_CLICK:
            log.info("DOUBLE CLICK")
            self._double_click()
        elif event == GestureEvent.RIGHT_CLICK:
            log.info("RIGHT CLICK")
            self._click_right()
        elif event == GestureEvent.DRAG_START:
            log.info("DRAG START")
            self._press_left()
        elif event == GestureEvent.DRAG_END:
            log.info("DRAG END")
            self._release_left()
        elif event == GestureEvent.SCROLL_UP:
            self.mouse.scroll(0, scroll_amount)
        elif event == GestureEvent.SCROLL_DOWN:
            self.mouse.scroll(0, -scroll_amount)

    # ── Safe button ops ───────────────────────────────────────

    def _press_left(self):
        if not self._btn_left_down:
            self.mouse.press(Button.left)
            self._btn_left_down = True

    def _release_left(self):
        if self._btn_left_down:
            self.mouse.release(Button.left)
            self._btn_left_down = False

    def _click_left(self):
        self._release_left()
        self.mouse.click(Button.left, 1)

    def _double_click(self):
        self._release_left()
        self.mouse.click(Button.left, 2)

    def _click_right(self):
        if self._btn_right_down:
            self.mouse.release(Button.right)
            self._btn_right_down = False
        self.mouse.click(Button.right, 1)

    def _release_all(self):
        self._release_left()
        if self._btn_right_down:
            self.mouse.release(Button.right)
            self._btn_right_down = False

    # ── Filter management ─────────────────────────────────────

    def _init_filters(self, t, x, y):
        self._fx = OneEuroFilter(t, x,
                                 min_cutoff=config.SMOOTHING_MIN_CUTOFF,
                                 beta=config.SMOOTHING_BETA)
        self._fy = OneEuroFilter(t, y,
                                 min_cutoff=config.SMOOTHING_MIN_CUTOFF,
                                 beta=config.SMOOTHING_BETA)

    def _reset_filters(self):
        self._fx = None
        self._fy = None

    # ── ESC key ───────────────────────────────────────────────

    def _on_key(self, key):
        if key == Key.esc:
            if self._safety is not None:
                self._safety.emergency_stop("ESC key")
            else:
                self.hard_stop()
