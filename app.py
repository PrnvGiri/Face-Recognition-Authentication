from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session
from src.camera import VideoCamera
from src.auth import AuthSystem
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random key for session

# Global instances
camera = VideoCamera()
auth_system = AuthSystem()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('welcome'))
        
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if auth_system.verify_password(username, password):
            session['user'] = username
            return redirect(url_for('welcome'))
        else:
            error = "Invalid username or password"
            
    return render_template('login.html', error=error)

@app.route('/api/camera_control', methods=['POST'])
def camera_control():
    action = request.json.get('action')
    if action == 'start':
        success = camera.start_camera()
        return jsonify({'success': success, 'message': 'Camera started' if success else 'Failed to start camera'})
    elif action == 'stop':
        camera.stop_camera()
        return jsonify({'success': True, 'message': 'Camera stopped'})
    return jsonify({'success': False, 'message': 'Invalid action'})

@app.route('/api/face_auth', methods=['POST'])
def face_auth():
    username = request.json.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Username required'})

    # Get latest detection from camera
    if not camera.last_detection:
        return jsonify({'success': False, 'message': 'No face detected'})
        
    detected_name = camera.last_detection.get('name')
    
    if detected_name == 'Unknown':
        return jsonify({'success': False, 'message': 'Face authentication failed: Unknown user'})
        
    if detected_name and detected_name.lower() == username.lower():
        session['user'] = username
        return jsonify({'success': True, 'redirect': url_for('welcome')})
    
    return jsonify({
        'success': False, 
        'message': f'Face authentication failed. Detected: {detected_name}, Expected: {username}'
    })

@app.route('/welcome')
def welcome():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('welcome.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/video_feed')
def video_feed():
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/last_detection')
def last_detection():
    return jsonify(camera.last_detection)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
