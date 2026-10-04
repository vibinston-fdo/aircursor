import cv2
import time
from src.vision.hand_tracker import HandTracker

def test_tracker():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    tracker.viz_mode = "ANALYSIS"
    
    print("Testing HandTracker...")
    
    printed = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        processed, hand_data = tracker.process_frame(frame)
        
        if hand_data and not printed:
            print("HAND DETECTED")
            print(f"NUMBER OF HANDS: {len(hand_data)}")
            lms = hand_data[0]['landmarks'].landmark
            print(f"LANDMARK COUNT: {len(lms)}")
            for i, lm in enumerate(lms):
                print(f"{i}: x={lm.x:.4f}, y={lm.y:.4f}")
            printed = True
            
        cv2.imshow("Test Tracker", processed)
        if cv2.waitKey(1) & 0xFF == 27:
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_tracker()
