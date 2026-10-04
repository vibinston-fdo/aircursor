"""
AirCursor Pro — Session Telemetry
Tracks usage statistics during a single session.
"""
import time

class SessionTelemetry:
    def __init__(self):
        self.start_time = time.time()
        self.frames_processed = 0
        self.left_clicks = 0
        self.right_clicks = 0
        self.double_clicks = 0
        self.drags = 0
        self.scrolls = 0
        self.safety_stops = 0

    def reset(self):
        self.__init__()

    def get_duration_s(self) -> float:
        return time.time() - self.start_time

    def get_stats(self) -> dict:
        dur = self.get_duration_s()
        return {
            "duration_s": dur,
            "frames": self.frames_processed,
            "avg_fps": (self.frames_processed / dur) if dur > 0 else 0.0,
            "left_clicks": self.left_clicks,
            "right_clicks": self.right_clicks,
            "double_clicks": self.double_clicks,
            "drags": self.drags,
            "scrolls": self.scrolls,
            "safety_stops": self.safety_stops
        }
