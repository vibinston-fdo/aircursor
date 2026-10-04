"""
Gesture Engine — Phase 5 Rewrite
=================================
Simplified, robust runtime gesture classifier.
"""

import time
import math
from dataclasses import dataclass, field
from enum import Enum, auto
from src.core import config
from src.core.logger import get_logger

log = get_logger("GestureEngine")

class GestureState(Enum):
    IDLE             = "IDLE"
    CURSOR_ACTIVE    = "CURSOR_ACTIVE"
    LEFT_CLICK       = "LEFT_CLICK"
    RIGHT_CLICK      = "RIGHT_CLICK"
    DRAG             = "DRAG"
    SCROLL           = "SCROLL"

class GestureEvent(Enum):
    NONE         = auto()
    LEFT_CLICK   = auto()
    RIGHT_CLICK  = auto()
    DOUBLE_CLICK = auto()
    DRAG_START   = auto()
    DRAG_END     = auto()
    SCROLL_UP    = auto()
    SCROLL_DOWN  = auto()

@dataclass
class GestureResult:
    state:              GestureState = GestureState.IDLE
    event:              GestureEvent = GestureEvent.NONE
    left_dist:          float        = 1.0
    right_dist:         float        = 1.0
    confidence:         float        = 0.0
    scroll_amount:      int          = 0
    is_scrolling:       bool         = False
    finger_states:      dict         = field(default_factory=dict)

# ── Geometry Helpers ─────────────────────────────────────────

def _lm(landmarks, idx):
    lm = landmarks.landmark[idx]
    return lm.x, lm.y, lm.z

def _dist3(a, b) -> float:
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

def _hand_size(landmarks) -> float:
    return max(_dist3(_lm(landmarks, 0), _lm(landmarks, 9)), 1e-6)

def _finger_open(landmarks, tip_idx: int, pip_idx: int) -> bool:
    """Rotation invariant: if tip is further from wrist than the PIP joint."""
    w = _lm(landmarks, 0)
    tip = _lm(landmarks, tip_idx)
    pip = _lm(landmarks, pip_idx)
    return _dist3(w, tip) > _dist3(w, pip)

def get_finger_states(landmarks) -> dict:
    if not landmarks:
        return {}
        
    # Thumb: distance from wrist to tip vs wrist to IP (idx 3)
    thumb_open = _finger_open(landmarks, 4, 3)
    
    return {
        "THUMB":  thumb_open,
        "INDEX":  _finger_open(landmarks, 8, 6),
        "MIDDLE": _finger_open(landmarks, 12, 10),
        "RING":   _finger_open(landmarks, 16, 14),
        "PINKY":  _finger_open(landmarks, 20, 18),
    }

class GestureEngine:
    def __init__(self):
        self.state = GestureState.IDLE
        self.is_dragging = False
        
        # Temporal smoothing
        self.candidate = GestureState.IDLE
        self.candidate_frames = 0
        
        # Timing
        self.pinch_start_time = 0.0
        self.last_click_time = 0.0
        self.last_scroll_time = 0.0
        self.scroll_ref_y = 0.0
        self.scroll_accum = 0.0

    def process(self, landmarks) -> GestureResult:
        now = time.time()
        
        if landmarks is None:
            return self._handle_loss(now)

        # 1. Geometry
        hs = _hand_size(landmarks)
        l_dist = _dist3(_lm(landmarks, 4), _lm(landmarks, 8)) / hs
        r_dist = _dist3(_lm(landmarks, 4), _lm(landmarks, 12)) / hs
        fs = get_finger_states(landmarks)
        
        # 2. Raw Classifications
        is_left_pinch = l_dist < 0.12   # Generous runtime thresholds for safety
        is_right_pinch = r_dist < 0.12
        
        is_scroll = (fs["INDEX"] and fs["MIDDLE"] and 
                     not fs["RING"] and not fs["PINKY"] and 
                     not is_left_pinch and not is_right_pinch)
                     
        is_cursor = (fs["INDEX"] and 
                     not is_scroll and 
                     not is_left_pinch and 
                     not is_right_pinch)

        # 3. Direct Classifier Rules
        raw_state = GestureState.IDLE
        
        if is_left_pinch:
            raw_state = GestureState.LEFT_CLICK
        elif is_right_pinch:
            raw_state = GestureState.RIGHT_CLICK
        elif is_scroll:
            raw_state = GestureState.SCROLL
        elif is_cursor:
            raw_state = GestureState.CURSOR_ACTIVE

        # 4. Temporal Stabilisation (3 frames)
        if raw_state == self.candidate:
            self.candidate_frames += 1
        else:
            self.candidate = raw_state
            self.candidate_frames = 1
            
        if self.candidate_frames >= 3:
            next_state = self.candidate
        else:
            next_state = self.state  # Hold old state
            
        # 5. Handle State Transitions & Events
        event = GestureEvent.NONE
        scroll_amt = 0
        
        # Drag logic overlay
        if next_state == GestureState.LEFT_CLICK:
            if self.state != GestureState.LEFT_CLICK and self.state != GestureState.DRAG:
                self.pinch_start_time = now
            elif (now - self.pinch_start_time) > 0.4:
                next_state = GestureState.DRAG
                
        # Emit Events based on transition
        if next_state == GestureState.LEFT_CLICK and self.state != GestureState.LEFT_CLICK:
            if (now - self.last_click_time) < 0.4:
                event = GestureEvent.DOUBLE_CLICK
                self.last_click_time = 0.0 # reset
            else:
                event = GestureEvent.LEFT_CLICK
                self.last_click_time = now
                
        elif next_state == GestureState.RIGHT_CLICK and self.state != GestureState.RIGHT_CLICK:
            event = GestureEvent.RIGHT_CLICK
            
        elif next_state == GestureState.DRAG and self.state != GestureState.DRAG:
            event = GestureEvent.DRAG_START
            self.is_dragging = True
            
        elif self.state == GestureState.DRAG and next_state not in (GestureState.DRAG, GestureState.LEFT_CLICK):
            event = GestureEvent.DRAG_END
            self.is_dragging = False
            
        elif next_state == GestureState.SCROLL:
            if self.state != GestureState.SCROLL:
                self.scroll_ref_y = landmarks.landmark[9].y
                self.scroll_accum = 0.0
            else:
                dy = landmarks.landmark[9].y - self.scroll_ref_y
                self.scroll_ref_y = landmarks.landmark[9].y
                self.scroll_accum += dy * 5.0 # Sens
                clicks = int(self.scroll_accum)
                if abs(clicks) >= 1 and (now - self.last_scroll_time) > 0.1:
                    self.scroll_accum -= clicks
                    self.last_scroll_time = now
                    scroll_amt = clicks
                    event = GestureEvent.SCROLL_DOWN if clicks > 0 else GestureEvent.SCROLL_UP
        
        self.state = next_state
        
        conf = 1.0 if self.state != GestureState.IDLE else 0.0

        return GestureResult(
            state=self.state,
            event=event,
            left_dist=l_dist,
            right_dist=r_dist,
            confidence=conf,
            scroll_amount=abs(scroll_amt),
            is_scrolling=(self.state == GestureState.SCROLL),
            finger_states=fs
        )
        
    def emergency_stop(self):
        self.state = GestureState.IDLE
        self.candidate = GestureState.IDLE
        self.is_dragging = False

    def _handle_loss(self, now):
        evt = GestureEvent.NONE
        if self.is_dragging:
            evt = GestureEvent.DRAG_END
        self.emergency_stop()
        return GestureResult(state=GestureState.IDLE, event=evt)
