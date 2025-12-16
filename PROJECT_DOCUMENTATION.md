# Face Security System - Technical Documentation

This document explains the technical architecture of the Face Security System.

---

## 1. System Overview

This application is a **Secure Web Portal** that gates access using two methods:
1.  **Something you know**: A Password.
2.  **Something you are**: Your Face.

It uses a Client-Server architecture where **Flask** (Python) runs the backend logic/AI, and the browser handles the User Interface.

---

## 2. Core Components

### Authentication (`src/auth.py`)
*   **Role**: The Gatekeeper.
*   **User Management**: It does not use a traditional SQL database. Instead, it scans the `src/FaceData` directory.
    *   If a folder exists named `Pranav`, then "Pranav" is a valid user.
*   **Password Logic**: Currently enforces a strict default password (`1234`) for all users for simplicity.

### Camera Controller (`src/camera.py`)
*   **Role**: Privacy & Performance Manager.
*   **On-Demand Logic**: Unlike typical surveillance apps, this camera **idles** by default.
    *   `start_camera()`: Called only when the User interacts with the "Face ID" UI.
    *   `stop_camera()`: Called immediately when the user leaves the tab or logs in successfully.
*   **Optimization**:
    *   **Frame Skipping**: Face Recognition is heavy. We only run the AI model once every 5 frames. This keeps the video feed smooth (30fps) while the AI thinks in the background (6fps).

### Face Detector (`src/detector.py`)
*   **Role**: The Brain.
*   **Technology**: Uses **FaceNet** (InceptionResnetV1).
*   **Process**:
    1.  **Detect**: Find the face box.
    2.  **Embed**: Convert the face into a 512-dimensional number vector.
    3.  **Compare**: Measure distance to known vectors in `src/face_model.pth`.

---

## 3. Workflow

### Face Login Flow
1.  User opens Login Page.
2.  User clicks "Face ID" tab -> Browser calls `/api/camera_control` (Action: Start).
3.  Server opens Webcam.
4.  User enters username "Pranav".
5.  Detector sees a face, identifies it as "Pranav".
6.  User clicks "Authenticate".
7.  Server compares `Detected Name` vs `Requested Name`.
8.  **Match**: Login Success -> Stop Camera -> Redirect to Welcome.
9.  **Mismatch**: Error Message.

---

## 4. File Structure

*   **`train_model.py`**: Run this once to learn new faces.
*   **`app.py`**: The web server. Connects the UI to the Logic.
*   **`src/`**: All backend logic.
*   **`templates/`**: HTML files.
*   **`static/`**: CSS styles.

---

## 5. Security & Performance
*   **Session Security**: Uses Flask's `secret_key` and server-side sessions to track logged-in users.
*   **Performance**: Frame skipping ensures the camera doesn't lag even on slower CPUs.
