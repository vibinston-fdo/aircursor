"""
Vision Worker — AirCursor Pro Phase 5
======================================
Background QThread. Integrates camera, hand tracker, gesture engine,
cursor controller, and performance timing into one pipeline.
"""

import cv2
import time
import traceback
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from src.vision.hand_tracker import HandTracker
from src.engine.gesture_engine import GestureEngine, GestureEvent, GestureState
from src.engine.mouse_controller import CursorController
from src.core import config
from src.core.config_manager import ConfigManager
from src.core.safety_controller import SafetyController
from src.core.logger import get_logger
from src.core.telemetry import SessionTelemetry

log = get_logger("Vision")


class VisionWorker(QThread):
    frame_ready    = pyqtSignal(object, object)   # (rgb ndarray, telemetry dict)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        super().__init__()
        self.camera_id = camera_id
        self.width     = width
        self.height    = height
        self.running   = True

        # Telemetry
        self.telemetry = SessionTelemetry()

        # Sub-systems
        self.cm = ConfigManager()
        self.cursor_ctrl  = CursorController()
        self.gesture_eng  = GestureEngine()

        # Wire up safety
        safety = SafetyController()
        safety.register_cursor(self.cursor_ctrl)
        safety.register_gesture(self.gesture_eng)
        # Note: telemetry can be exposed to safety for resetting
        self.cursor_ctrl.set_safety(safety)
        self.safety = safety

        # UI toggles
        self.debug_view    = False
        self.gesture_debug = False

    def run(self):
        log.info("Vision worker starting")
        self.status_changed.emit("Initializing Camera...")
        
        self.telemetry.reset()

        cap = None
        try:
            cap = self._open_camera()
            if cap is None:
                return

            self.status_changed.emit("Initializing Hand Tracker...")
            tracker = HandTracker(
                detection_con=config.DETECTION_CONFIDENCE,
                tracking_con=config.TRACKING_CONFIDENCE,
            )
            log.info("Hand tracker ready")
            self.status_changed.emit("Running")

            prev_t   = time.perf_counter()
            fps      = 0.0

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    self.error_occurred.emit("Camera read failed — reconnecting...")
                    log.warning("Camera read failed")
                    time.sleep(0.5)
                    continue

                self.telemetry.frames_processed += 1
                frame_t0 = time.perf_counter()
                frame    = cv2.flip(frame, 1)

                viz_mode = self.cm.get("PERF_MODE", "STANDARD")
                
                # Tell HandTracker if we want drawing
                tracker.viz_mode = viz_mode

                ht_t0 = time.perf_counter()
                processed, hand_data = tracker.process_frame(frame)
                ht_ms = (time.perf_counter() - ht_t0) * 1000.0

                rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)

                now = time.perf_counter()
                dt  = now - prev_t
                if dt > 0:
                    fps = fps * config.FPS_SMOOTHING + (1.0 / dt) * (1.0 - config.FPS_SMOOTHING)
                prev_t = now

                ge_t0     = time.perf_counter()
                landmarks = hand_data[0]['landmarks'] if hand_data else None
                gesture   = self.gesture_eng.process(landmarks)
                ge_ms     = (time.perf_counter() - ge_t0) * 1000.0

                if gesture.event == GestureEvent.LEFT_CLICK:
                    self.telemetry.left_clicks += 1
                elif gesture.event == GestureEvent.RIGHT_CLICK:
                    self.telemetry.right_clicks += 1
                elif gesture.event == GestureEvent.DOUBLE_CLICK:
                    self.telemetry.double_clicks += 1

                # Let gestures classify and show in UI even if cursor_ctrl is off

                index_pos  = None
                mapped_pos = None

                if hand_data:
                    lm  = hand_data[0]['landmarks']
                    tip = lm.landmark[8]
                    index_pos = (tip.x, tip.y)

                    if self.cursor_ctrl.enabled and \
                       not gesture.is_scrolling:
                        mapped_pos = self.cursor_ctrl.process(
                            tip.x, tip.y,
                            gesture.event,
                            self.gesture_eng.is_dragging,
                            gesture.scroll_amount,
                        )
                    elif self.cursor_ctrl.enabled and gesture.is_scrolling:
                        self.telemetry.scrolls += 1
                        self.cursor_ctrl.process(
                            tip.x, tip.y,
                            gesture.event,
                            False,
                            gesture.scroll_amount,
                        )
                        mapped_pos = self.cursor_ctrl.last_screen_pos
                else:
                    self.cursor_ctrl.on_hand_lost()
                    self.gesture_eng.emergency_stop()

                if self.gesture_eng.is_dragging:
                    self.telemetry.drags += 1

                if viz_mode != "PERFORMANCE" or self.gesture_debug:
                    self._draw_debug(rgb, index_pos, landmarks, viz_mode)

                cursor_status = self._cursor_status(gesture)
                frame_ms = (time.perf_counter() - frame_t0) * 1000.0

                telemetry_dict = {
                    "fps":          fps,
                    "hand_data":    hand_data,
                    "cursor_status": cursor_status,
                    "index_pos":    index_pos,
                    "mapped_pos":   mapped_pos,
                    "frame_ms":     frame_ms,
                    "ht_ms":        ht_ms,
                    "ge_ms":        ge_ms,
                    "cursor_rate":  self.cursor_ctrl.update_rate,
                    "cursor_proc":  self.cursor_ctrl.proc_time_ms,
                    "gesture_state": gesture.state.name,
                    "gesture_event": gesture.event.name,
                    "gesture_conf":  gesture.confidence,
                    "left_dist":     gesture.left_dist,
                    "right_dist":    gesture.right_dist,
                    "is_dragging":   self.gesture_eng.is_dragging,
                    "is_scrolling":  gesture.is_scrolling,
                    "scroll_amount": gesture.scroll_amount,
                    "finger_states": gesture.finger_states,
                    "session_stats": self.telemetry.get_stats(),
                }

                self.frame_ready.emit(rgb, telemetry_dict)

        except Exception as e:
            msg = f"{e}\n{traceback.format_exc()}"
            log.error(f"Vision worker exception: {msg}")
            self.error_occurred.emit(str(e))
        finally:
            if cap and cap.isOpened():
                cap.release()
                log.info("Camera released")
            self.status_changed.emit("Stopped")

    def stop(self):
        log.info("Vision worker stopping")
        self.running = False
        self.cursor_ctrl.hard_stop()
        self.wait()

    def _open_camera(self):
        cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            msg = f"Could not open camera {self.camera_id}"
            log.error(msg)
            self.error_occurred.emit(msg)
            return None

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        log.info(f"Camera {self.camera_id} opened at {self.width}x{self.height}")
        return cap

    def _draw_debug(self, rgb, index_pos, landmarks, viz_mode):
        h, w, _ = rgb.shape
        if viz_mode == "ANALYSIS" or self.gesture_debug:
            cv2.rectangle(
                rgb,
                (int(config.TRACK_LEFT * w),  int(config.TRACK_TOP * h)),
                (int(config.TRACK_RIGHT * w), int(config.TRACK_BOTTOM * h)),
                (100, 149, 237), 2,
            )
            if landmarks:
                tt = landmarks.landmark[4]
                mt = landmarks.landmark[12]
                cv2.circle(rgb, (int(tt.x*w), int(tt.y*h)), 8, (255, 165, 0), -1)
                cv2.circle(rgb, (int(mt.x*w), int(mt.y*h)), 8, (0, 255, 255), -1)
        
        if index_pos and viz_mode != "MINIMAL":
            cv2.circle(rgb, (int(index_pos[0]*w), int(index_pos[1]*h)), 10, (0, 0, 255), -1)

    def _cursor_status(self, gesture) -> str:
        if not self.cursor_ctrl.enabled:
            return "DISABLED"
        if gesture.is_scrolling:
            return "SCROLLING"
        if self.gesture_eng.is_dragging:
            return "DRAGGING"
        if gesture.state.name in ("LEFT_CLICK", "RIGHT_CLICK", "DRAG"):
            return "GESTURE"
        return "ACTIVE"
