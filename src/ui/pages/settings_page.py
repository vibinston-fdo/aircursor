"""
Settings Page — Central Configuration
"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFrame, QLabel, QScrollArea, QWidget, QGridLayout, 
    QComboBox, QSlider
)
from PyQt6.QtCore import Qt

from src.ui.pages.base_page import BasePage
from src.ui import components, styles
from src.core.config_manager import ConfigManager
from src.core import config


class SettingsPage(BasePage):
    def __init__(self, app_context):
        super().__init__(app_context)
        self.cm = ConfigManager()
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Settings")
        title.setFont(components.QFont("Segoe UI", 24, components.QFont.Weight.Bold))
        title.setStyleSheet("color: #c9d1d9;")
        lay.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        c_lay = QVBoxLayout(content)
        c_lay.setSpacing(20)

        # Build sections based on Phase 4 spec
        self._build_section(c_lay, "Camera", [
            ("Camera Device", self._make_combo(["0", "1", "2"], str(config.CAMERA_ID))),
            ("Processing Resolution", self._make_label(f"{config.FRAME_WIDTH}x{config.FRAME_HEIGHT}")),
        ])

        self._build_section(c_lay, "Tracking", [
            ("Detection Confidence", self._make_slider("DETECTION_CONFIDENCE", 30, 100)),
            ("Tracking Confidence", self._make_slider("TRACKING_CONFIDENCE", 30, 100)),
        ])

        self._build_section(c_lay, "Cursor", [
            ("Smoothing Min Cutoff", self._make_slider("SMOOTHING_MIN_CUTOFF", 5, 500, 100.0)),
            ("Smoothing Beta", self._make_slider("SMOOTHING_BETA", 0, 5000, 100.0)),
            ("Deadzone (px)", self._make_slider("DEADZONE", 0, 2000, 100.0)),
        ])

        self._build_section(c_lay, "Gestures", [
            ("Scroll Sensitivity", self._make_slider("SCROLL_SENSITIVITY", 50, 2000, 100.0)),
            ("Pinch Confirm (ms)", self._make_slider("PINCH_CONFIRMATION_TIME", 20, 500, 1000.0)),
            ("Drag Hold (ms)", self._make_slider("DRAG_HOLD_TIME", 100, 2000, 1000.0)),
            ("Click Cooldown (ms)", self._make_slider("CLICK_COOLDOWN", 100, 1000, 1000.0)),
        ])

        self._build_section(c_lay, "Interface", [
            ("Performance Mode", self._make_combo(["ANALYSIS", "STANDARD", "MINIMAL"], config.PERF_MODE, "PERF_MODE")),
        ])

        self._build_section(c_lay, "Safety", [
            ("Emergency Key", self._make_label("ESC")),
        ])

        c_lay.addStretch()
        scroll.setWidget(content)
        lay.addWidget(scroll)

    def _build_section(self, layout: QVBoxLayout, title: str, items: list):
        f = QFrame()
        f.setStyleSheet(styles.PANEL_STYLE)
        l = QVBoxLayout(f)
        l.addWidget(components.section_label(title.upper()))
        
        g = QGridLayout()
        g.setColumnStretch(1, 1)
        for row, (name, widget) in enumerate(items):
            g.addWidget(components.key_label(name), row, 0)
            g.addWidget(widget, row, 1)
        
        l.addLayout(g)
        layout.addWidget(f)

    def _make_label(self, text: str):
        lbl = components.val_label(text)
        return lbl

    def _make_combo(self, items: list, current: str, key: str = None):
        cb = QComboBox()
        cb.addItems(items)
        cb.setCurrentText(current)
        cb.setStyleSheet("QComboBox { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 4px; padding: 4px; }")
        if key:
            cb.currentTextChanged.connect(lambda text, k=key: self._on_combo_change(k, text))
        return cb
        
    def _on_combo_change(self, key, text):
        self.cm.set(key, text)
        self.cm.save()

    def _make_slider(self, key: str, min_v: int, max_v: int, scale: float = 100.0):
        # We use a horizontal layout with a slider and a value label
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_v)
        slider.setMaximum(max_v)
        
        val = self.cm.get(key)
        slider.setValue(int(val * scale))
        
        lbl = components.val_label(f"{val:.2f}")
        lbl.setFixedWidth(60)
        
        slider.valueChanged.connect(lambda v, k=key, s=scale, l=lbl: self._on_slider_change(k, v, s, l))
        
        lay.addWidget(slider)
        lay.addWidget(lbl)
        return w

    def _on_slider_change(self, key, value, scale, lbl):
        real_val = value / scale
        if self.cm.set(key, real_val):
            lbl.setText(f"{real_val:.2f}")
            self.cm.save()
