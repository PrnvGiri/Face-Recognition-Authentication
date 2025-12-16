from src.detector import FaceDetector
import os

def train():
    print("Starting model training (embedding generation)...")
    
    # Initialize detector
    detector = FaceDetector()
    
    # Load faces from the raw images directory
    detector.load_known_faces()
    
    # Save the model
    model_path = 'src/face_model.pth'
    detector.save_model(model_path)
    
    print(f"\nTraining complete! Model saved to {model_path}")
    print("You can now run 'main.py' to start the security system.")

if __name__ == "__main__":
    train()
