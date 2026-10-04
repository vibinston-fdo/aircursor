# AIRCURSOR PRO
*Control Your Computer. Without Touching It.*

**Vision-Based Touchless Human-Computer Interaction**

AirCursor Pro is a professional, low-latency Computer Vision system that converts hand gestures into direct Windows Operating System actions. Using modern MediaPipe Hand Landmarks tracking and a custom, debounced state-machine gesture engine, it achieves real-time, responsive pointer control without relying on physical peripherals.

## Features

- **Real-Time Pointer Control:** Navigate your screen fluidly using your index finger.
- **Gesture State Machine:** Accurately distinguishes between intent and noise using dynamic debouncing.
- **Integrated Calibration Wizard:** Easily define an ergonomic camera-to-screen tracking zone.
- **Scrolling & Dragging:** Emulates scroll wheels and held mouse buttons securely.
- **Global Safety Controller:** Guaranteed instant control-release with a centralized Emergency Stop.
- **Expo Demo Mode:** Guided demonstrations, real-time performance metrics, and clean UI for public demonstrations.
- **Dynamic Configuration:** Adjust sensitivity, deadzones, and processing performance levels dynamically.

---

## Gesture Controls

| Intended Action | Gesture |
| --- | --- |
| **Move Cursor** | Point and move your **Index Finger** |
| **Left Click** | Pinch your **Thumb and Index Finger** |
| **Right Click** | Pinch your **Thumb and Middle Finger** |
| **Double Click** | Perform two quick consecutive pinches |
| **Click & Drag** | **Pinch and Hold**, then move your hand |
| **Scroll Mode** | Extend **Index and Middle Fingers (Peace Sign)** and move vertically |

---

## Architecture & Technology Stack

**Technology Stack:**
- **Python 3.14** (Core execution environment)
- **OpenCV** (Camera capture, frame preprocessing, and fast visualization)
- **MediaPipe Tasks API** (Machine Learning hand landmark inference)
- **PyQt6** (Asynchronous User Interface)
- **pynput** (System-level mouse control)
- **NumPy** (Math and coordinate mapping calculations)

**Processing Pipeline:**
1. **Threaded Capture:** Asynchronously read camera frames to prevent blocking the UI.
2. **Inference:** Extract 21 3D hand coordinates using the `HandLandmarker` model.
3. **Filtering:** Apply exponential smoothing (derived from the 1€ Filter concept) to eliminate noise.
4. **Gesture Engine:** Determine user intent through normalized pinch distances and temporal history mapping.
5. **Cursor Action:** Map coordinates and inject system actions securely.

---

## Installation & Running

1. **Clone the repository.**
2. **Activate your Python environment** (Ensure Python 3.10+):
   ```powershell
   .\venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
4. **Run the Application:**
   ```powershell
   python src/main.py
   ```

---

## Configuration & Calibration

AirCursor Pro works immediately, but tracking spaces vary based on user distance and webcam FOV. 
- Open the **Calibration Tab** to interactively define the four corners of your tracking zone. This ensures natural, comfortable finger movement spans your entire monitor space.
- Open the **Settings Tab** to adjust click cooldowns, scroll sensitivity, processing resolution, and visual performance modes.

*Settings are securely saved and restored across sessions.*

---

## Safety Systems

AirCursor Pro is built for unguided public demonstrations. 

1. **Emergency Stop (ESC):** At any time, pressing `ESC` engages the `SafetyController`. This immediately revokes mouse control, releases any held OS clicks/drags, and halts gesture processing until manually restarted.
2. **Hand-Loss Recovery:** If tracking is lost mid-action (e.g., someone walks in front of the camera, or you drop your hand during a drag), the system proactively releases the mouse and transitions to a safe idle state.
3. **MAX_HANDS Enforced:** Hardcoded to track exactly one hand, preventing chaotic background interference.

---

## Known Limitations

- **Lighting Dependency:** Deeply backlit environments (e.g., pointing the camera directly at a sunlit window) degrade MediaPipe's confidence matrix significantly.
- **FPS Constraints:** While the inference engine easily processes frames under `25ms`, generic webcams are physically hardware-locked to output exactly 30 FPS.

## License

This project is developed for Expo demonstration purposes.
