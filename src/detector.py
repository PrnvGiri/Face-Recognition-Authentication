import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np
from PIL import Image
import os

class FaceDetector:
    def __init__(self):
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        print(f"Running on device: {self.device}")
        
        # Initialize MTCNN
        self.mtcnn = MTCNN(keep_all=True, device=self.device)
        
        # Initialize InceptionResnetV1 for recognition
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        self.known_embeddings = []
        self.known_names = []
        
    def load_model(self, model_path):
        """Loads known faces from a saved model file."""
        if os.path.exists(model_path):
            print(f"Loading model from {model_path}...")
            try:
                checkpoint = torch.load(model_path)
                self.known_embeddings = checkpoint['embeddings']
                self.known_names = checkpoint['names']
                print(f"Model loaded. {len(self.known_names)} known faces.")
            except Exception as e:
                print(f"Error loading model: {e}")
        else:
            print(f"Model file {model_path} not found.")

    def save_model(self, model_path):
        """Saves the current known faces to a file."""
        if len(self.known_embeddings) == 0:
            print("No embeddings to save.")
            return
            
        print(f"Saving model to {model_path}...")
        torch.save({
            'embeddings': self.known_embeddings,
            'names': self.known_names
        }, model_path)
        print("Model saved successfully.")

    def load_known_faces(self):
        """Loads faces from the src/FaceData directory (supports subdirectories)."""
        data_dir = 'src/FaceData'
        if not os.path.exists(data_dir):
            print(f"Warning: {data_dir} not found.")
            return

        print("Loading known faces...")
        # Walk through subdirectories
        for root, dirs, files in os.walk(data_dir):
            for filename in files:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    path = os.path.join(root, filename)
                    
                    # Use folder name as person name if inside a subdir, else filename
                    if root != data_dir:
                        name = os.path.basename(root)
                    else:
                        name = os.path.splitext(filename)[0]
                    
                    try:
                        img = Image.open(path)
                        # Get embedding
                        # Use a separate MTCNN instance for alignment to ensure consistent behavior
                        # Or just use the existing one but handle output carefully
                        
                        # For known faces, we expect 1 face. keep_all=True might return list.
                        img_cropped = self.mtcnn(img)
                        
                        if img_cropped is not None:
                            # Handle different return types of MTCNN
                            if isinstance(img_cropped, list):
                                # List of tensors
                                if len(img_cropped) > 0:
                                    face_tensor = img_cropped[0]
                                else:
                                    continue
                            else:
                                # Single tensor (already stacked or single face)
                                # If it's 4D [N, 3, 160, 160], take first
                                if img_cropped.ndim == 4:
                                    face_tensor = img_cropped[0]
                                else:
                                    face_tensor = img_cropped
                            
                            # Ensure 4D batch for ResNet
                            if face_tensor.ndim == 3:
                                face_tensor = face_tensor.unsqueeze(0)
                                
                            face_tensor = face_tensor.to(self.device)
                            embedding = self.resnet(face_tensor).detach().cpu()
                            
                            self.known_embeddings.append(embedding)
                            self.known_names.append(name)
                            print(f"Loaded: {name} from {filename}")
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        print(f"Error loading {filename}: {e}")
        
        if self.known_embeddings:
            self.known_embeddings = torch.cat(self.known_embeddings)
            print(f"Total known faces: {len(self.known_names)}")
        else:
            print("No known faces loaded.")

    def recognize(self, frame):
        """
        Detects and recognizes faces in a frame.
        Args:
            frame: A numpy array representing the image (RGB).
        Returns:
            boxes: List of bounding boxes.
            names: List of names corresponding to boxes.
            probs: List of detection probabilities.
        """
        try:
            img = Image.fromarray(frame)
            
            # Detect faces (get boxes and probs)
            boxes, probs = self.mtcnn.detect(img)
            
            names = []
            if boxes is not None:
                # Get aligned face crops
                faces_aligned = self.mtcnn(img)
                
                if faces_aligned is not None:
                    # Prepare batch for ResNet
                    if isinstance(faces_aligned, list):
                        faces_tensor = torch.stack(faces_aligned).to(self.device)
                    elif faces_aligned.ndim == 4:
                         faces_tensor = faces_aligned.to(self.device)
                    else:
                        # Single 3D tensor
                        faces_tensor = faces_aligned.unsqueeze(0).to(self.device)

                    embeddings = self.resnet(faces_tensor).detach().cpu()
                    
                    # Compare with known embeddings
                    for i, embedding in enumerate(embeddings):
                        name = "Unknown"
                        if len(self.known_embeddings) > 0:
                            # Calculate distances
                            distances = (embedding - self.known_embeddings).norm(p=2, dim=1)
                            min_dist = distances.min()
                            
                            # Threshold
                            if min_dist < 0.6:
                                min_index = distances.argmin()
                                name = self.known_names[min_index]
                        
                        names.append(name)
            
            return boxes, names, probs
            
        except Exception as e:
            print(f"Error during recognition: {e}")
            return None, None, None

    def detect(self, frame):
        # Legacy support or simple detection
        boxes, names, probs = self.recognize(frame)
        return boxes, probs
