# Secure Face Authentication System

A secure biometric login system featuring **Face Recognition (Face ID)** and **Password** authentication. Built with Flask, OpenCV, and PyTorch (FaceNet).

## Features
- **Biometric Login**: Secure Face ID using `FaceNet` embeddings.
- **Dual Auth**: Password fallback (Default: `1234`).
- **Smart Camera**: Active only on demand; privacy-first design.
- **Responsive UI**: Modern Dark Mode interface.

## Quick Start

### 1. Setup
```bash
# Clone
git clone <repo-url>

# Install
pip install -r requirements.txt
```

### 2. Add User
- Create folder: `src/FaceData/YourName`
- Add photos.
- Train:
```bash
python train_model.py
```

### 3. Run
```bash
python app.py
```
Visit: [http://localhost:5000](http://localhost:5000)

## Project Layout
- `app.py`: Main Server.
- `src/`: Core Logic (Camera, Auth, Detector).
- `templates/`: Frontend Views.
- `static/`: Assets (CSS).

## Tech Stack
- **Python** (Flask)
- **OpenCV** (Vision)
- **PyTorch** (FaceNet AI)
