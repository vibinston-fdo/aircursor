"""
AirCursor Pro — Reusable UI Components
"""
from PyQt6.QtWidgets import QLabel, QFrame, QPushButton, QHBoxLayout, QWidget, QSlider
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from src.ui import styles

def h_sep():
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setStyleSheet("color: #30363d; background: #30363d; border: none; max-height: 1px;")
    return sep

def section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    lbl.setStyleSheet("color: #6e7681; letter-spacing: 1px;")
    return lbl

def val_label(text="—") -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI Mono", 10, QFont.Weight.Bold))
    lbl.setStyleSheet("color: #c9d1d9;")
    return lbl

def key_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI", 10))
    lbl.setStyleSheet("color: #8b949e;")
    return lbl

def title_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
    lbl.setStyleSheet("color: #58a6ff;")
    return lbl

def subtitle_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI", 11))
    lbl.setStyleSheet("color: #6e7681;")
    return lbl

def create_button(text: str, is_toggle=False, is_danger=False) -> QPushButton:
    btn = QPushButton(text)
    btn.setCheckable(is_toggle)
    btn.setStyleSheet(styles.BTN_DANGER if is_danger else styles.BTN_OFF)
    return btn

def update_toggle_button(btn: QPushButton, text: str, checked: bool):
    btn.setText(text)
    btn.setStyleSheet(styles.BTN_ON if checked else styles.BTN_OFF)
