# Secure Face Authentication System

A secure login system offering both **Face Recognition** (Face ID) and **Password** authentication, featuring a modern dark-themed UI and on-demand camera control.

## Features
- **Dual Authentication**:
    - **Password**: Standard secure login (Default: `1234`).
    - **Face ID**: secure biometric login using `FaceNet` embeddings.
- **Folder-Based User Management**:
    - Users are defined simply by creating a folder in `src/FaceData/Username`.
    - Strict name matching: You can only login if your face matches the requested username.
- **On-Demand Camera**:
    - Privacy-focused: Camera remains **OFF** by default.
    - Activates only when the "Face ID" tab is selected.
    - Automatically stops upon successful login or tab switch.
- **Modern UI**:
    - Premium dark mode design.
    - Responsive animations and feedback.

## Installation

1.  **Clone/Download** this repository.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## How to Use

### 1. Add Users
To create a valid user:
1.  Create a folder inside `src/FaceData` with the person's name (e.g., `src/FaceData/Pranav`).
2.  Add clear photos of their face to that folder.
3.  **Train the Model**:
    ```bash
    python train_model.py
    ```

### 2. Start the System
Run the Flask server:
```bash
python app.py
```

### 3. Login
Open [http://localhost:5000/login](http://localhost:5000/login).
- **Password Option**: Enter username "Pranav" and password `INTELLIPAAT`.
- **Face ID Option**: Switch tab, enter "Pranav", and click "Authenticate". The camera will turn on, verify your face, and log you in.

## Project Structure
- `app.py`: Main Flask application handling routes and API.
- `src/auth.py`: Handles user verification (Usernames from folders, fixed Password).
- `src/camera.py`: Manages webcam stream, face detection, and frame skipping optimizations.
- `src/detector.py`: Core AI logic using FaceNet.
- `templates/`:
    - `login.html`: The main login interface.
    - `welcome.html`: Secure page after login.
- `static/style.css`: Modern styling.

## Technologies
- **Python & Flask**
- **PyTorch & FaceNet** (AI)
- **OpenCV** (Camera)
- **HTML5/CSS3** (Frontend)
