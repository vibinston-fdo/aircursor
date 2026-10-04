"""
About & Technology Page
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QFrame, QLabel, QScrollArea, QWidget, QGridLayout, QHBoxLayout
)
from PyQt6.QtGui import QFont, QPixmap, QImage
from PyQt6.QtCore import Qt
import numpy as np

from src.ui.pages.base_page import BasePage
from src.ui import components, styles
from src.core import config

class AboutPage(BasePage):
    def __init__(self, app_context):
        super().__init__(app_context)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 40, 40, 40)
        
        # Header
        title = QLabel(config.APP_TITLE)
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #58a6ff;")
        lay.addWidget(title)

        subtitle = QLabel("Vision-Based Touchless Human-Computer Interaction")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #8b949e;")
        lay.addWidget(subtitle)
        lay.addWidget(components.h_sep())
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        c_lay = QVBoxLayout(content)
        c_lay.setSpacing(20)
        
        # Tech Stack
        stack_lbl = components.section_label("TECHNOLOGY STACK")
        c_lay.addWidget(stack_lbl)
        
        stack_text = QLabel(
            "• Python 3.14\n"
            "• OpenCV (Computer Vision)\n"
            "• MediaPipe Tasks API (Hand Landmark Detection)\n"
            "• PyQt6 (User Interface)\n"
            "• pynput (Windows OS Control)"
        )
        stack_text.setStyleSheet("color: #c9d1d9; font-size: 13px; line-height: 1.5;")
        c_lay.addWidget(stack_text)
        
        c_lay.addWidget(components.h_sep())
        
        # Pipeline
        pipe_lbl = components.section_label("PIPELINE ARCHITECTURE")
        c_lay.addWidget(pipe_lbl)
        
        pipeline = (
            "WEBCAM\n"
            "  ↓\n"
            "FRAME CAPTURE & PREPROCESSING\n"
            "  ↓\n"
            "MEDIA-PIPE HAND LANDMARK DETECTION\n"
            "  ↓\n"
            "FINGER & JOINT ANALYSIS (21-Points)\n"
            "  ↓\n"
            "GESTURE RECOGNITION (Debounced State Machine)\n"
            "  ↓\n"
            "CURSOR & MOUSE CONTROLLER (Euro Filter Smoothing)\n"
            "  ↓\n"
            "WINDOWS OS CONTROL"
        )
        pipe_text = QLabel(pipeline)
        pipe_text.setFont(QFont("Segoe UI Mono", 11, QFont.Weight.Bold))
        pipe_text.setStyleSheet("color: #58a6ff; background: #21262d; padding: 16px; border-radius: 8px;")
        c_lay.addWidget(pipe_text)
        
        c_lay.addWidget(components.h_sep())
        
        # Telemetry Box
        c_lay.addWidget(components.section_label("SESSION TELEMETRY (LIVE)"))
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(10)
        
        self.lbls = {}
        keys = ["Session Duration", "Frames Processed", "Average FPS", "Left Clicks", 
                "Right Clicks", "Double Clicks", "Drags", "Scrolls", "Safety Stops"]
                
        for row, k in enumerate(keys):
            lbl = components.val_label("0")
            self.lbls[k] = lbl
            self.stats_grid.addWidget(components.key_label(k + ":"), row, 0)
            self.stats_grid.addWidget(lbl, row, 1)
            
        c_lay.addLayout(self.stats_grid)
        
        c_lay.addStretch()
        scroll.setWidget(content)
        lay.addWidget(scroll)

    def on_frame(self, rgb: np.ndarray, tel: dict):
        stats = tel.get('session_stats', {})
        if not stats:
            return
            
        dur = stats.get("duration_s", 0)
        mins, secs = divmod(int(dur), 60)
        
        self.lbls["Session Duration"].setText(f"{mins:02d}:{secs:02d}")
        self.lbls["Frames Processed"].setText(f"{stats.get('frames', 0):,}")
        self.lbls["Average FPS"].setText(f"{stats.get('avg_fps', 0):.1f}")
        self.lbls["Left Clicks"].setText(str(stats.get('left_clicks', 0)))
        self.lbls["Right Clicks"].setText(str(stats.get('right_clicks', 0)))
        self.lbls["Double Clicks"].setText(str(stats.get('double_clicks', 0)))
        self.lbls["Drags"].setText(str(stats.get('drags', 0)))
        self.lbls["Scrolls"].setText(str(stats.get('scrolls', 0)))
        self.lbls["Safety Stops"].setText(str(stats.get('safety_stops', 0)))
