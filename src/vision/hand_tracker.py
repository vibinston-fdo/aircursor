"""
Hand Tracker using MediaPipe Tasks API
"""
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

_MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "hand_landmarker.task"))

class HandTracker:
    def __init__(self, max_hands=1, detection_con=0.7, tracking_con=0.7):
        base_options = python.BaseOptions(model_asset_path=_MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_tracking_confidence=tracking_con
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

        # Connect pairs for drawing
        self.connections = [
            (0,1), (1,2), (2,3), (3,4),       # Thumb
            (0,5), (5,6), (6,7), (7,8),       # Index
            (5,9), (9,10), (10,11), (11,12),  # Middle
            (9,13), (13,14), (14,15), (15,16),# Ring
            (13,17), (17,18), (18,19), (19,20),# Pinky
            (0,17)                            # Palm
        ]

        self.viz_mode = "STANDARD"

    def process_frame(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        results = self.detector.detect(mp_image)
        
        hand_data = []
        if results.hand_landmarks:
            for hand_idx, landmarks in enumerate(results.hand_landmarks):
                # The gesture engine expects an object with `.landmark[i].x/y/z`
                class DummyLandmark:
                    def __init__(self, x, y, z):
                        self.x, self.y, self.z = x, y, z
                class DummyHandLandmarks:
                    def __init__(self, lms):
                        self.landmark = [DummyLandmark(lm.x, lm.y, lm.z) for lm in lms]

                adapted_landmarks = DummyHandLandmarks(landmarks)
                
                h, w, _ = frame.shape
                x_min, y_min = w, h
                x_max, y_max = 0, 0
                
                # Draw connections and calculate bbox
                if self.viz_mode in ("STANDARD", "ANALYSIS"):
                    for connection in self.connections:
                        start_idx = connection[0]
                        end_idx = connection[1]
                        
                        lm_start = landmarks[start_idx]
                        lm_end = landmarks[end_idx]
                        
                        x1, y1 = int(lm_start.x * w), int(lm_start.y * h)
                        x2, y2 = int(lm_end.x * w), int(lm_end.y * h)
                        
                        cv2.line(frame, (x1, y1), (x2, y2), (200, 200, 200), 2)
                
                for i, lm in enumerate(landmarks):
                    x, y = int(lm.x * w), int(lm.y * h)
                    
                    if self.viz_mode == "ANALYSIS":
                        cv2.circle(frame, (x, y), 4, (0, 0, 255), -1)
                    elif self.viz_mode == "STANDARD" and i in [4, 8, 12, 16, 20]: # Fingertips only
                        cv2.circle(frame, (x, y), 5, (0, 200, 0), -1)
                        
                    x_min = min(x_min, x)
                    y_min = min(y_min, y)
                    x_max = max(x_max, x)
                    y_max = max(y_max, y)
                
                padding = 20
                bbox = (max(0, x_min - padding), max(0, y_min - padding), 
                        min(w, x_max + padding), min(h, y_max + padding))
                
                # handedness
                handedness_list = results.handedness[hand_idx]
                label = handedness_list[0].category_name
                score = handedness_list[0].score
                
                hand_data.append({
                    'landmarks': adapted_landmarks,
                    'bbox': bbox,
                    'label': label,
                    'score': score
                })
                
                if self.viz_mode == "ANALYSIS":
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} {score:.2f}", (bbox[0], bbox[1] - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
        return frame, hand_data
