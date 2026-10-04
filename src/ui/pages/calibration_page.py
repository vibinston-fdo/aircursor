"""
Calibration Page — Tracking Area Definition
"""
import time
import numpy as np
import cv2
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QGridLayout
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

from src.ui.pages.base_page import BasePage
from src.ui import components, styles
from src.core.config_manager import ConfigManager
from src.core import config
from src.core.logger import get_logger

log = get_logger("Calibration")

# State
CAL_IDLE = 0
CAL_TL   = 1
CAL_TR   = 2
CAL_BR   = 3
CAL_BL   = 4
CAL_DONE = 5

class CalibrationPage(BasePage):
    def __init__(self, app_context):
        super().__init__(app_context)
        self.cm = ConfigManager()
        self.state = CAL_IDLE
        self.points = {}
        self.stable_frames = 0
        self.last_pos = None
        self._setup_ui()

    def _setup_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(10)
        self._video = QLabel("Camera")
        self._video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video.setStyleSheet(styles.VIDEO_STYLE)
        self._video.setMinimumSize(config.FRAME_WIDTH, config.FRAME_HEIGHT)
        left.addWidget(self._video, 1)

        right = QFrame()
        right.setFixedWidth(320)
        right.setStyleSheet(styles.PANEL_STYLE)
        r_lay = QVBoxLayout(right)
        r_lay.setContentsMargins(16, 16, 16, 16)
        r_lay.setSpacing(12)

        r_lay.addWidget(components.section_label("CALIBRATION WIZARD"))
        
        self._lbl_instr = QLabel("Define your tracking area to map\nfinger movement to the screen.")
        self._lbl_instr.setStyleSheet("color: #8b949e;")
        r_lay.addWidget(self._lbl_instr)

        self._btn_start = components.create_button("START CALIBRATION")
        self._btn_start.clicked.connect(self._start_cal)
        r_lay.addWidget(self._btn_start)

        self._btn_reset = components.create_button("RESET TO DEFAULT", is_danger=True)
        self._btn_reset.clicked.connect(self._reset_cal)
        r_lay.addWidget(self._btn_reset)

        r_lay.addWidget(components.h_sep())
        r_lay.addWidget(components.section_label("STATUS"))
        
        self._lbl_step = components.val_label("Not Started")
        self._lbl_hold = components.val_label("—")
        r_lay.addWidget(self._lbl_step)
        r_lay.addWidget(self._lbl_hold)

        r_lay.addStretch()

        outer.addLayout(left, 1)
        outer.addWidget(right)

    def _start_cal(self):
        self.state = CAL_TL
        self.points.clear()
        self.stable_frames = 0
        self.last_pos = None
        self._btn_start.setText("RESTART CALIBRATION")
        self._lbl_step.setText("POINT 1: TOP LEFT")
        self._lbl_hold.setText("Hold steady...")
        log.info("Calibration started")

    def _reset_cal(self):
        self.cm.reset_to_defaults()
        self.cm.save()
        self.state = CAL_IDLE
        self._btn_start.setText("START CALIBRATION")
        self._lbl_step.setText("Reset to Default")
        self._lbl_hold.setText("—")
        log.info("Calibration reset to default")

    def on_frame(self, rgb: np.ndarray, tel: dict):
        # Draw on copy
        frame = rgb.copy()
        h, w, _ = frame.shape

        if self.state in (CAL_TL, CAL_TR, CAL_BR, CAL_BL):
            self._process_calibration(frame, tel, w, h)

        # Draw current bounds if idle/done
        if self.state in (CAL_IDLE, CAL_DONE):
            cv2.rectangle(
                frame,
                (int(config.TRACK_LEFT * w),  int(config.TRACK_TOP * h)),
                (int(config.TRACK_RIGHT * w), int(config.TRACK_BOTTOM * h)),
                (100, 149, 237), 2,
            )

        qt_img = QImage(frame.data, w, h, w*3, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(
            self._video.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._video.setPixmap(pix)

    def _process_calibration(self, frame, tel, w, h):
        # Draw target corners
        pts = {
            CAL_TL: (int(w*0.1), int(h*0.1)),
            CAL_TR: (int(w*0.9), int(h*0.1)),
            CAL_BR: (int(w*0.9), int(h*0.9)),
            CAL_BL: (int(w*0.1), int(h*0.9)),
        }
        target = pts[self.state]
        cv2.circle(frame, target, 20, (255, 255, 0), 2)
        cv2.putText(frame, "TARGET", (target[0]-30, target[1]-30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        ip = tel.get('index_pos')
        if not ip:
            self.stable_frames = 0
            self._lbl_hold.setText("Tracking Lost")
            self._lbl_hold.setStyleSheet(f"color: {styles.COLOR_ERROR};")
            return

        ix, iy = int(ip[0]*w), int(ip[1]*h)
        cv2.circle(frame, (ix, iy), 10, (0, 0, 255), -1)

        if self.last_pos:
            dist = np.hypot(ip[0] - self.last_pos[0], ip[1] - self.last_pos[1])
            if dist < 0.02:  # steady finger
                self.stable_frames += 1
            else:
                self.stable_frames = 0
        self.last_pos = ip

        prog = min(100, int((self.stable_frames / 30) * 100))
        self._lbl_hold.setText(f"Hold steady: {prog}%")
        self._lbl_hold.setStyleSheet(f"color: {styles.COLOR_WARN};")

        # Draw progress bar on video
        cv2.rectangle(frame, (ix-20, iy+20), (ix-20 + int(40 * (prog/100)), iy+25), (0, 255, 0), -1)

        if self.stable_frames >= 30:
            self.points[self.state] = ip
            self.stable_frames = 0
            self._next_state()

    def _next_state(self):
        if self.state == CAL_TL:
            self.state = CAL_TR
            self._lbl_step.setText("POINT 2: TOP RIGHT")
        elif self.state == CAL_TR:
            self.state = CAL_BR
            self._lbl_step.setText("POINT 3: BOTTOM RIGHT")
        elif self.state == CAL_BR:
            self.state = CAL_BL
            self._lbl_step.setText("POINT 4: BOTTOM LEFT")
        elif self.state == CAL_BL:
            self._finish_calibration()

    def _finish_calibration(self):
        tl = self.points[CAL_TL]
        tr = self.points[CAL_TR]
        br = self.points[CAL_BR]
        bl = self.points[CAL_BL]

        # Calculate bounding box
        min_x = min(tl[0], bl[0])
        max_x = max(tr[0], br[0])
        min_y = min(tl[1], tr[1])
        max_y = max(bl[1], br[1])

        # Validate
        if max_x - min_x > 0.1 and max_y - min_y > 0.1:
            self.cm.set("TRACK_LEFT", min_x)
            self.cm.set("TRACK_RIGHT", max_x)
            self.cm.set("TRACK_TOP", min_y)
            self.cm.set("TRACK_BOTTOM", max_y)
            self.cm.set("CALIBRATION_VALID", True)
            self.cm.set("CALIBRATION_DATE", time.strftime("%Y-%m-%d %H:%M"))
            self.cm.save()
            self._lbl_step.setText("CALIBRATION SAVED ✓")
            self._lbl_hold.setText("—")
            self._lbl_hold.setStyleSheet(f"color: {styles.COLOR_ACTIVE};")
            log.info(f"Calibration successful: L={min_x:.2f} R={max_x:.2f} T={min_y:.2f} B={max_y:.2f}")
        else:
            self._lbl_step.setText("CALIBRATION FAILED")
            self._lbl_hold.setText("Area too small. Try again.")
            self._lbl_hold.setStyleSheet(f"color: {styles.COLOR_ERROR};")
            log.warning("Calibration failed: area too small")

        self.state = CAL_DONE
        self._btn_start.setText("RECALIBRATE")
