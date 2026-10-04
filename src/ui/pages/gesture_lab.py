"""
Gesture Lab — Visualisation and Debugging
"""
import numpy as np
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFrame, QLabel, QGridLayout, QWidget
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

from src.ui.pages.base_page import BasePage
from src.ui import components, styles
from src.core import config


class GestureLabPage(BasePage):
    def __init__(self, app_context):
        super().__init__(app_context)
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
        r_lay.setSpacing(8)

        r_lay.addWidget(components.section_label("GESTURE LAB"))

        # STATE MACHINE
        g1 = QGridLayout(); g1.setSpacing(6)
        self._lbl_state = components.val_label("IDLE")
        self._lbl_event = components.val_label("NONE")
        self._lbl_conf  = components.val_label("0%")
        g1.addWidget(components.key_label("State:"), 0, 0)
        g1.addWidget(self._lbl_state, 0, 1)
        g1.addWidget(components.key_label("Event:"), 1, 0)
        g1.addWidget(self._lbl_event, 1, 1)
        g1.addWidget(components.key_label("Confidence:"), 2, 0)
        g1.addWidget(self._lbl_conf, 2, 1)
        r_lay.addLayout(g1)
        r_lay.addWidget(components.h_sep())

        # PINCH DISTANCES
        r_lay.addWidget(components.section_label("PINCH DISTANCES"))
        g2 = QGridLayout(); g2.setSpacing(6)
        self._lbl_ldist = components.val_label("—")
        self._lbl_rdist = components.val_label("—")
        g2.addWidget(components.key_label("Thumb ↔ Index:"), 0, 0)
        g2.addWidget(self._lbl_ldist, 0, 1)
        g2.addWidget(components.key_label("Thumb ↔ Middle:"), 1, 0)
        g2.addWidget(self._lbl_rdist, 1, 1)
        r_lay.addLayout(g2)
        r_lay.addWidget(components.h_sep())

        # FINGER STATES
        r_lay.addWidget(components.section_label("FINGER STATES"))
        g3 = QGridLayout(); g3.setSpacing(6)
        self._fingers = {}
        for row, name in enumerate(["THUMB", "INDEX", "MIDDLE", "RING", "PINKY"]):
            lbl = components.val_label("—")
            self._fingers[name] = lbl
            g3.addWidget(components.key_label(name), row, 0)
            g3.addWidget(lbl, row, 1)
        r_lay.addLayout(g3)
        r_lay.addWidget(components.h_sep())

        # DATA
        r_lay.addWidget(components.section_label("DIAGNOSTICS"))
        g4 = QGridLayout(); g4.setSpacing(6)
        self._lbl_ix = components.val_label("—")
        self._lbl_iy = components.val_label("—")
        g4.addWidget(components.key_label("HAND:"), 0, 0)
        g4.addWidget(self._lbl_ix, 0, 1)
        g4.addWidget(components.key_label("LANDMARKS:"), 1, 0)
        g4.addWidget(self._lbl_iy, 1, 1)
        r_lay.addLayout(g4)

        r_lay.addStretch()

        outer.addLayout(left, 1)
        outer.addWidget(right)

    def on_frame(self, rgb: np.ndarray, tel: dict):
        h, w, ch = rgb.shape

        # Always draw gesture debug in Gesture Lab
        if self.worker and not self.worker.gesture_debug:
            self.worker.gesture_debug = True

        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(
            self._video.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._video.setPixmap(pix)

        # Update labels
        self._lbl_state.setText(tel.get('gesture_state', 'IDLE'))
        self._lbl_event.setText(tel.get('gesture_event', 'NONE'))
        self._lbl_conf.setText(f"{tel.get('gesture_conf', 0)*100:.0f}%")

        self._lbl_ldist.setText(f"{tel.get('left_dist', 0):.3f}")
        self._lbl_rdist.setText(f"{tel.get('right_dist', 0):.3f}")

        ip = tel.get('index_pos')

        fs = tel.get('finger_states', {})
        for name, lbl in self._fingers.items():
            if not fs:
                lbl.setText("—")
                lbl.setStyleSheet(f"color: {styles.COLOR_IDLE};")
                continue
            is_open = fs.get(name, False)
            if is_open:
                lbl.setText("OPEN")
                lbl.setStyleSheet(f"color: {styles.COLOR_ACTIVE};")
            else:
                lbl.setText("CLOSED")
                lbl.setStyleSheet(f"color: {styles.COLOR_WARN};")

        # PHASE K EXTRA DIAGNOSTICS (Temporary addition)
        hd = tel.get('hand_data')
        if hd:
            self._lbl_ix.setText("DETECTED")
            self._lbl_iy.setText("21")
        else:
            self._lbl_ix.setText("NOT DETECTED")
            self._lbl_iy.setText("0")

    def on_hide(self):
        if self.worker:
            self.worker.gesture_debug = False
