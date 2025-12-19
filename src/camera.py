import cv2
from src.detector import FaceDetector
from src.alert import AlertSystem
import time
import numpy as np

class VideoCamera:
    def __init__(self):
        # Init
        self.detector = FaceDetector()
        self.detector.load_model('src/face_model.pth')
        self.alert_system = AlertSystem()
        self.last_detection = None
        self.video = None
        self.is_running = False
        self.frame_count = 0
        self.detection_interval = 5  # Interval
        self.last_boxes = None
        self.last_names = None
        self.last_probs = None

    def clear_history(self):
        """Reset state"""
        self.last_detection = None
        self.last_boxes = None
        self.last_names = None
        self.last_probs = None
        self.frame_count = 0

    def start_camera(self):
        if self.is_running and self.video is not None:
             return True
             
        # Capture
        print("Starting camera...")
        self.clear_history()  # Reset
        self.video = cv2.VideoCapture(1)
        if not self.video.isOpened():
            # Fallback
            self.video = cv2.VideoCapture(0)
        
        if self.video.isOpened():
            self.is_running = True
            print("Camera started.")
            return True
        else:
            print("Failed to open camera.")
            return False

    def stop_camera(self):
        if self.video is not None:
            self.video.release()
            self.video = None
        self.is_running = False
        self.clear_history() # Reset
        print("Camera stopped.")

    def __del__(self):
        self.stop_camera()

    def get_frame(self):
        if not self.is_running or self.video is None:
            # Off state
            blank_image = np.zeros((480, 640, 3), np.uint8)
            cv2.putText(blank_image, "Camera Off", (200, 240), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, jpeg = cv2.imencode('.jpg', blank_image)
            return jpeg.tobytes()

        success, frame = self.video.read()
        if not success:
            return None

        # BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        self.frame_count += 1
        
        # Check Faces
        if self.frame_count % self.detection_interval == 0 or self.last_boxes is None:
            self.last_boxes, self.last_names, self.last_probs = self.detector.recognize(frame_rgb)
        
        # Results
        boxes, names, probs = self.last_boxes, self.last_names, self.last_probs
        
        # Draw
        if boxes is not None:
            for box, name, prob in zip(boxes, names, probs):
                # Color
                if name == "Unknown":
                    color = (0, 0, 255) # Red
                else:
                    color = (0, 255, 0) # Green

                x1, y1, x2, y2 = [int(b) for b in box]
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                label = f"{name} ({prob:.2f})"
                cv2.putText(frame, label, (x1, y1 - 10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Update
                if self.frame_count % self.detection_interval == 0:
                    self.last_detection = {
                        'name': name,
                        'time': time.strftime('%H:%M:%S'),
                        'type': 'known' if name != "Unknown" else 'unknown'
                    }
            
            # Alert
            if self.frame_count % self.detection_interval == 0:
                 self.alert_system.trigger(len(boxes))
        else:
            # No face
            if self.frame_count % self.detection_interval == 0:
                self.last_detection = None

        # Encode
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
