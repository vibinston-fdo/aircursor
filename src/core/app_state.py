"""
AirCursor Pro — Application State
Maintains the high-level application state for UI reflection.
"""
from enum import Enum, auto

class AppState(Enum):
    STARTING    = auto()
    READY       = auto()
    TRACKING    = auto()
    PAUSED      = auto()
    CALIBRATING = auto()
    ERROR       = auto()
    STOPPED     = auto()
