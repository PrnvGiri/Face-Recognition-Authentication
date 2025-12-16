import cv2
from src.detector import FaceDetector
from src.alert import AlertSystem
import time
import numpy as np

class VideoCamera:
    def __init__(self):
        # Initialize components
        self.detector = FaceDetector()
        self.detector.load_model('src/face_model.pth')
        self.alert_system = AlertSystem()
        self.last_detection = None
        self.video = None
        self.is_running = False
        self.frame_count = 0
        self.detection_interval = 5  # Run detection every 5 frames
        self.last_boxes = None
        self.last_names = None
        self.last_probs = None

    def start_camera(self):
        if self.is_running and self.video is not None:
             return True
             
        # Start video capture
        print("Starting camera...")
        self.video = cv2.VideoCapture(1)
        if not self.video.isOpened():
            # Fallback to 0 if 1 fails
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
        self.frame_count = 0
        self.last_boxes = None
        print("Camera stopped.")

    def __del__(self):
        self.stop_camera()

    def get_frame(self):
        if not self.is_running or self.video is None:
            # Return a black frame or None if camera is off
            # Creating a blank image for the placeholder
            blank_image = np.zeros((480, 640, 3), np.uint8)
            cv2.putText(blank_image, "Camera Off", (200, 240), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, jpeg = cv2.imencode('.jpg', blank_image)
            return jpeg.tobytes()

        success, frame = self.video.read()
        if not success:
            return None

        # Convert BGR to RGB for MTCNN
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        self.frame_count += 1
        
        # Detect and Recognize faces (Skip frames)
        if self.frame_count % self.detection_interval == 0 or self.last_boxes is None:
            self.last_boxes, self.last_names, self.last_probs = self.detector.recognize(frame_rgb)
        
        # Use existing results (either fresh or cached)
        boxes, names, probs = self.last_boxes, self.last_names, self.last_probs
        
        # Process detections
        if boxes is not None:
            for box, name, prob in zip(boxes, names, probs):
                # Determine color: Green for Known, Red for Unknown
                if name == "Unknown":
                    color = (0, 0, 255) # Red
                else:
                    color = (0, 255, 0) # Green

                # Draw bounding box
                x1, y1, x2, y2 = [int(b) for b in box]
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Add label
                label = f"{name} ({prob:.2f})"
                cv2.putText(frame, label, (x1, y1 - 10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Update last detection
                # Only update if it's a fresh detection to keep it accurate to the frame
                if self.frame_count % self.detection_interval == 0:
                    self.last_detection = {
                        'name': name,
                        'time': time.strftime('%H:%M:%S'),
                        'type': 'known' if name != "Unknown" else 'unknown'
                    }
            
            # Trigger alert
            if self.frame_count % self.detection_interval == 0:
                 self.alert_system.trigger(len(boxes))

        # Encode frame to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
