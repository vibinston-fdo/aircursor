"""
Main Page — Professional Dashboard & Expo Mode
"""
import numpy as np
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFrame, QGridLayout, QLabel, QWidget, QPushButton
)
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer

from src.ui.pages.base_page import BasePage
from src.ui import components, styles
from src.core import config
from src.core.logger import get_logger

log = get_logger("MainPage")

DEMO_STEPS = [
    "STEP 1: Show your hand to the camera.",
    "STEP 2: Move your index finger to control the cursor.",
    "STEP 3: Pinch thumb + index finger to left-click.",
    "STEP 4: Pinch thumb + middle finger to right-click.",
    "STEP 5: Hold thumb + index finger to drag.",
    "STEP 6: Raise index + middle fingers to scroll."
]


class MainPage(BasePage):
    def __init__(self, app_context):
        super().__init__(app_context)
        self.demo_step = -1
        self._setup_ui()

    def _setup_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        # ── Left: Video & Banner ─────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(10)
        
        header = QLabel("AIRCURSOR PRO")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #c9d1d9; letter-spacing: 2px;")
        
        sub = QLabel("Vision-Based Touchless Human-Computer Interaction")
        sub.setFont(QFont("Segoe UI", 11))
        sub.setStyleSheet("color: #8b949e;")
        
        left.addWidget(header)
        left.addWidget(sub)

        # Video
        self._video = QLabel("Initializing Camera...")
        self._video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video.setStyleSheet(styles.VIDEO_STYLE)
        self._video.setMinimumSize(config.FRAME_WIDTH, config.FRAME_HEIGHT)
        left.addWidget(self._video, 1)
        
        # Guided Demo Banner
        self._demo_banner = QLabel("")
        self._demo_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._demo_banner.setFixedHeight(50)
        self._demo_banner.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._demo_banner.setStyleSheet(styles.BANNER_BASE + "background-color: #1f6feb; color: #ffffff;")
        self._demo_banner.hide()
        left.addWidget(self._demo_banner)

        # ── Right: Panels ────────────────────────────────────────
        right = QFrame()
        right.setFixedWidth(340)
        right.setStyleSheet(styles.PANEL_STYLE)
        r_lay = QVBoxLayout(right)
        r_lay.setContentsMargins(20, 20, 20, 20)
        r_lay.setSpacing(16)

        # CURRENT GESTURE
        r_lay.addWidget(components.section_label("CURRENT GESTURE"))
        self._lbl_event = QLabel("NO GESTURE")
        self._lbl_event.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._lbl_event.setStyleSheet("color: #8b949e; margin-bottom: -5px;")
        
        self._lbl_event_desc = QLabel("Waiting for hand...")
        self._lbl_event_desc.setFont(QFont("Segoe UI", 10))
        self._lbl_event_desc.setStyleSheet("color: #6e7681; margin-bottom: 10px;")
        self._lbl_event_desc.setWordWrap(True)
        
        r_lay.addWidget(self._lbl_event)
        r_lay.addWidget(self._lbl_event_desc)
        r_lay.addWidget(components.h_sep())

        # SYSTEM STATUS
        r_lay.addWidget(components.section_label("SYSTEM STATUS"))
        g1 = QGridLayout(); g1.setSpacing(8); g1.setColumnStretch(1, 1)

        self._lbl_cam    = components.val_label("Connecting...")
        self._lbl_track  = components.val_label("Waiting...")
        self._lbl_cursor = components.val_label("STANDBY")
        self._lbl_safety = components.val_label("ARMED ✓")
        self._lbl_safety.setStyleSheet(f"color: {styles.COLOR_ACTIVE};")

        g1.addWidget(components.key_label("Camera:"), 0, 0)
        g1.addWidget(self._lbl_cam, 0, 1)
        g1.addWidget(components.key_label("Hand Tracking:"), 1, 0)
        g1.addWidget(self._lbl_track, 1, 1)
        g1.addWidget(components.key_label("Cursor:"), 2, 0)
        g1.addWidget(self._lbl_cursor, 2, 1)
        g1.addWidget(components.key_label("Safety System:"), 3, 0)
        g1.addWidget(self._lbl_safety, 3, 1)
        
        r_lay.addLayout(g1)
        r_lay.addWidget(components.h_sep())

        # PERFORMANCE
        r_lay.addWidget(components.section_label("PERFORMANCE"))
        g3 = QGridLayout(); g3.setSpacing(6); g3.setColumnStretch(1, 1)
        self._lbl_fps = components.val_label("0.0")
        self._lbl_p_frame = components.val_label("0.0 ms")
        self._lbl_p_track = components.val_label("0.0 ms")

        g3.addWidget(components.key_label("FPS:"), 0, 0)
        g3.addWidget(self._lbl_fps, 0, 1)
        g3.addWidget(components.key_label("Total Frame:"), 1, 0)
        g3.addWidget(self._lbl_p_frame, 1, 1)
        g3.addWidget(components.key_label("Tracking inference:"), 2, 0)
        g3.addWidget(self._lbl_p_track, 2, 1)
        r_lay.addLayout(g3)

        r_lay.addStretch()

        # CONTROLS
        self._btn_cursor = components.create_button("▶ START CONTROL", is_toggle=True)
        self._btn_cursor.setMinimumHeight(45)
        self._btn_cursor.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._btn_cursor.clicked.connect(self._toggle_cursor)
        
        self._btn_demo = components.create_button("GUIDED DEMO", is_toggle=False)
        self._btn_demo.clicked.connect(self._next_demo_step)

        self._btn_stop = components.create_button("EMERGENCY STOP (ESC)", is_danger=True)
        self._btn_stop.clicked.connect(self._emergency_stop)
        
        self._btn_reset = components.create_button("RESET SESSION")
        self._btn_reset.setStyleSheet("background: #21262d; border: 1px solid #30363d; color: #c9d1d9; border-radius: 6px; padding: 6px;")
        self._btn_reset.clicked.connect(self._reset_session)

        r_lay.addWidget(self._btn_cursor)
        
        sub_ctrls = QHBoxLayout()
        sub_ctrls.addWidget(self._btn_demo)
        sub_ctrls.addWidget(self._btn_reset)
        r_lay.addLayout(sub_ctrls)
        
        r_lay.addWidget(self._btn_stop)

        outer.addLayout(left, 1)
        outer.addWidget(right)

    def _toggle_cursor(self, checked: bool):
        if self.worker:
            # Check safety config first
            if checked:
                # Pre-flight check
                if self._lbl_cam.text() != "Running":
                    self._btn_cursor.setChecked(False)
                    self._lbl_event.setText("CAMERA ERROR")
                    self._lbl_event_desc.setText("Cannot start control without a running camera.")
                    self._lbl_event.setStyleSheet(f"color: {styles.COLOR_ERROR};")
                    return
                if not self.worker.cm.get("CALIBRATION_VALID", False):
                    # Warning but allow
                    pass

            self.worker.cursor_ctrl.enabled = checked
            components.update_toggle_button(
                self._btn_cursor,
                "■ SYSTEM ACTIVE" if checked else "▶ START CONTROL",
                checked
            )
            log.info(f"Cursor control set to {checked}")

    def _emergency_stop(self):
        log.warning("Emergency Stop requested from UI")
        if self.worker:
            self.worker.safety.emergency_stop()
            self._btn_cursor.setChecked(False)
            self._toggle_cursor(False)
            
            self._lbl_event.setText("EMERGENCY STOP")
            self._lbl_event_desc.setText("All controls disengaged safely.")
            self._lbl_event.setStyleSheet(f"color: {styles.COLOR_ERROR};")

    def _reset_session(self):
        log.info("Reset session clicked")
        if self.worker:
            self.worker.telemetry.reset()
            self.worker.safety.reset_session()
            self._btn_cursor.setChecked(False)
            self._toggle_cursor(False)
            self.demo_step = -1
            self._demo_banner.hide()
            self._lbl_event.setText("SESSION RESET")
            self._lbl_event_desc.setText("All states cleared.")
            self._lbl_event.setStyleSheet("color: #8b949e;")

    def _next_demo_step(self):
        self.demo_step += 1
        if self.demo_step >= len(DEMO_STEPS):
            self.demo_step = -1
            self._demo_banner.hide()
            self._btn_demo.setText("GUIDED DEMO")
            return
            
        self._demo_banner.setText(DEMO_STEPS[self.demo_step])
        self._demo_banner.show()
        self._btn_demo.setText("NEXT STEP")
        
        if self.demo_step == 1 and not self._btn_cursor.isChecked():
            self._btn_cursor.setChecked(True)
            self._toggle_cursor(True)

    def on_frame(self, rgb: np.ndarray, tel: dict):
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(
            self._video.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._video.setPixmap(pix)

        ev = tel.get('gesture_event', 'NONE')
        is_scrolling = tel.get('is_scrolling', False)
        is_dragging = tel.get('is_dragging', False)

        if is_scrolling:
            self._lbl_event.setText("SCROLLING")
            self._lbl_event_desc.setText("Vertical movement translated to scroll wheel.")
            self._lbl_event.setStyleSheet(f"color: {styles.COLOR_HIGHLIGHT};")
        elif is_dragging:
            self._lbl_event.setText("DRAGGING")
            self._lbl_event_desc.setText("Pinch held. Mouse button locked down.")
            self._lbl_event.setStyleSheet(f"color: {styles.COLOR_HIGHLIGHT};")
        elif ev == 'LEFT_CLICK':
            self._lbl_event.setText("LEFT CLICK")
            self._lbl_event_desc.setText("Thumb + index finger pinch.")
            self._lbl_event.setStyleSheet(f"color: {styles.COLOR_ACTIVE};")
        elif ev == 'RIGHT_CLICK':
            self._lbl_event.setText("RIGHT CLICK")
            self._lbl_event_desc.setText("Thumb + middle finger pinch.")
            self._lbl_event.setStyleSheet(f"color: {styles.COLOR_ACTIVE};")
        elif ev == 'DOUBLE_CLICK':
            self._lbl_event.setText("DOUBLE CLICK")
            self._lbl_event_desc.setText("Two rapid pinches detected.")
            self._lbl_event.setStyleSheet(f"color: {styles.COLOR_ACTIVE};")
        elif ev == 'NONE':
            if tel.get('index_pos') and tel.get('cursor_status') == 'ACTIVE':
                self._lbl_event.setText("INDEX CONTROL")
                self._lbl_event_desc.setText("Moving cursor with index tip.")
                self._lbl_event.setStyleSheet(f"color: #c9d1d9;")
            elif not tel.get('index_pos'):
                if self._lbl_event.text() not in ("EMERGENCY STOP", "SESSION RESET"):
                    self._lbl_event.setText("NO GESTURE")
                    self._lbl_event_desc.setText("Waiting for hand...")
                    self._lbl_event.setStyleSheet("color: #8b949e;")

        self._lbl_fps.setText(f"{tel['fps']:.1f}")

        hd = tel['hand_data']
        if hd:
            self._lbl_track.setText("● ACTIVE")
            self._lbl_track.setStyleSheet(f"color: {styles.COLOR_ACTIVE};")
        else:
            self._lbl_track.setText("○ SEARCHING")
            self._lbl_track.setStyleSheet(f"color: {styles.COLOR_WARN};")

        cs = tel['cursor_status']
        c_col = {
            "ACTIVE":    styles.COLOR_ACTIVE,
            "DRAGGING":  styles.COLOR_HIGHLIGHT,
            "SCROLLING": styles.COLOR_HIGHLIGHT,
            "GESTURE":   styles.COLOR_WARN,
            "DISABLED":  styles.COLOR_IDLE,
        }.get(cs, styles.COLOR_IDLE)
        self._lbl_cursor.setText(cs)
        self._lbl_cursor.setStyleSheet(f"color: {c_col};")

        self._lbl_p_frame.setText(f"{tel.get('frame_ms', 0):.1f} ms")
        self._lbl_p_track.setText(f"{tel.get('ht_ms', 0):.1f} ms")
        
        if self.worker and not self.worker.cursor_ctrl.enabled and self._btn_cursor.isChecked():
            self._btn_cursor.setChecked(False)
            self._toggle_cursor(False)

    def set_camera_status(self, status: str):
        self._lbl_cam.setText(status)
        col = styles.COLOR_ACTIVE if status == "Running" else styles.COLOR_IDLE
        self._lbl_cam.setStyleSheet(f"color: {col};")

    def set_camera_error(self, msg: str):
        self._lbl_cam.setText("ERROR")
        self._lbl_cam.setStyleSheet(f"color: {styles.COLOR_ERROR};")
        self._video.setText(f"Camera Error:\n{msg}")
