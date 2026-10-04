"""
Base Page Class
"""
from PyQt6.QtWidgets import QWidget
import numpy as np

class BasePage(QWidget):
    def __init__(self, app_context=None):
        super().__init__()
        self.app_context = app_context
        self.worker = app_context.worker if app_context else None

    def on_frame(self, rgb: np.ndarray, tel: dict):
        pass

    def on_show(self):
        pass

    def on_hide(self):
        pass
