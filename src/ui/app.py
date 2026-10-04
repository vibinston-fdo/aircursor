"""
AirCursor Pro — Main Application UI (Phase 4)
Orchestrates pages, navigation, and the background vision worker.
"""
import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QPushButton, QFrame, QLabel
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QTimer

from src.core import config
from src.core.logger import get_logger
from src.vision.vision_worker import VisionWorker
from src.ui import styles

from src.ui.pages.main_page import MainPage
from src.ui.pages.calibration_page import CalibrationPage
from src.ui.pages.gesture_lab import GestureLabPage
from src.ui.pages.settings_page import SettingsPage
from src.ui.pages.about_page import AboutPage

log = get_logger("App")


class AppContext:
    def __init__(self, worker: VisionWorker):
        self.worker = worker


class AirCursorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{config.APP_TITLE} (Expo Mode)")
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(styles.APP_STYLE)

        self._start_worker()
        self.ctx = AppContext(self.worker)
        self._setup_ui()

    def _start_worker(self):
        log.info("Starting background vision worker")
        self.worker = VisionWorker(
            camera_id=config.CAMERA_ID,
            width=config.FRAME_WIDTH,
            height=config.FRAME_HEIGHT
        )
        self.worker.frame_ready.connect(self._on_frame)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.status_changed.connect(self._on_status)
        self.worker.start()

    def _setup_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Sidebar Navigation ────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #161b22; border-right: 1px solid #30363d;")
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(20, 30, 20, 20)
        sb_lay.setSpacing(10)

        title = QLabel(config.APP_TITLE)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #58a6ff; border: none;")
        sb_lay.addWidget(title)
        
        sb_lay.addSpacing(20)

        self.nav_btns = []
        self._create_nav_btn(sb_lay, "Dashboard", 0)
        self._create_nav_btn(sb_lay, "Calibration", 1)
        self._create_nav_btn(sb_lay, "Gesture Lab", 2)
        self._create_nav_btn(sb_lay, "Settings", 3)
        self._create_nav_btn(sb_lay, "About / Tech", 4)
        
        sb_lay.addStretch()
        
        version = QLabel(f"v{config.APP_VERSION} PRO")
        version.setStyleSheet("color: #6e7681; border: none;")
        sb_lay.addWidget(version)

        # ── Content Area ──────────────────────────────────────────
        content = QFrame()
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(20, 20, 20, 20)
        
        self.stack = QStackedWidget()
        self.pages = [
            MainPage(self.ctx),
            CalibrationPage(self.ctx),
            GestureLabPage(self.ctx),
            SettingsPage(self.ctx),
            AboutPage(self.ctx)
        ]
        
        for p in self.pages:
            self.stack.addWidget(p)
            
        content_lay.addWidget(self.stack)

        outer.addWidget(sidebar)
        outer.addWidget(content, 1)

        # Init selection
        self._switch_page(0)

    def _create_nav_btn(self, layout, text: str, index: int):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setStyleSheet(styles.NAV_BTN)
        btn.clicked.connect(lambda _, i=index: self._switch_page(i))
        self.nav_btns.append(btn)
        layout.addWidget(btn)

    def _switch_page(self, index: int):
        for i, btn in enumerate(self.nav_btns):
            btn.setChecked(i == index)
            
        old_idx = self.stack.currentIndex()
        if old_idx >= 0:
            self.pages[old_idx].on_hide()
            
        self.stack.setCurrentIndex(index)
        self.pages[index].on_show()

    def _on_frame(self, rgb: np.ndarray, tel: dict):
        idx = self.stack.currentIndex()
        if idx >= 0:
            self.pages[idx].on_frame(rgb, tel)

    def _on_error(self, msg: str):
        # Pass to main page to show in UI
        if isinstance(self.pages[0], MainPage):
            self.pages[0].set_camera_error(msg)

    def _on_status(self, status: str):
        if isinstance(self.pages[0], MainPage):
            self.pages[0].set_camera_status(status)

    def closeEvent(self, event):
        log.info("Application shutting down...")
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop()
        event.accept()

def run_app():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = AirCursorApp()
    win.show()
    sys.exit(app.exec())
