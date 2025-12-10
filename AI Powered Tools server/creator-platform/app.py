import os
import sys
import json
import uuid
import subprocess
from datetime import datetime
from werkzeug.utils import secure_filename
import shutil

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Initialize cache manager
from cache_manager import CacheManager 

# Create Flask application instance FIRST
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload

# Initialize CORS
CORS(app)


cache_manager = CacheManager(
    cache_dir=os.path.join(app.config['UPLOAD_FOLDER'], 'cache'),
    max_size_gb=10
)

# Now you can define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video-editor')
def video_editor():
    return render_template('video-editor.html')

@app.route('/creator-tool')
def creator_tool():
    return render_template('creator-tool.html')

@app.route('/code-assistant')
def code_assistant():
    return render_template('code-assistant.html')

# THEN define the upload route
@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Handle file upload - videos and images"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Rest of your upload function...

    # Check file extension
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    
    # Check if it's an image
    is_image = request.form.get('is_image') == 'true' or file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    if is_image:
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    else:
        allowed_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m4v']
    
    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Unsupported file format: {file_ext}'}), 400

    # Generate unique ID for this session
    session_id = session.get('session_id', str(uuid.uuid4()))
    session['session_id'] = session_id

    # Create session directory
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)

    # Save original file
    original_path = os.path.join(session_dir, filename)
    file.save(original_path)

    if is_image:
        # For images, just return the path
        try:
            from PIL import Image
            # Get image info
            with Image.open(original_path) as img:
                width, height = img.size
                
            response_data = {
                'success': True,
                'session_id': session_id,
                'original_filename': filename,
                'cached_path': f"/static/uploads/{session_id}/{filename}",
                'type': 'image',
                'width': width,
                'height': height,
                'resolution': f"{width}x{height}",
                'file_size': os.path.getsize(original_path),
                'duration': 0  # Images have no duration
            }
        except Exception as e:
            print(f"Image error: {e}")
            # Fallback if PIL fails
            response_data = {
                'success': True,
                'session_id': session_id,
                'original_filename': filename,
                'cached_path': f"/static/uploads/{session_id}/{filename}",
                'type': 'image',
                'width': 0,
                'height': 0,
                'resolution': '0x0',
                'file_size': os.path.getsize(original_path),
                'duration': 0
            }
    else:
        # For videos, use existing logic
        video_info = cache_manager.get_video_info(original_path)
        
        if not video_info:
            return jsonify({'error': 'Could not read video file'}), 400

        response_data = {
            'success': True,
            'session_id': session_id,
            'original_filename': filename,
            'cached_path': f"/static/uploads/{session_id}/{filename}",
            'type': 'video',
            'duration': video_info['duration'],
            'resolution': video_info['resolution'],
            'file_size': video_info['file_size']
        }

        # Start background processing for non-MP4 videos
        if file_ext in ['.mkv', '.avi', '.flv', '.wmv']:
            import threading
            threading.Thread(
                target=cache_manager.create_cached_version,
                args=(original_path, session_id),
                daemon=True
            ).start()
        else:
            cached_info = cache_manager.create_cached_version(original_path, session_id)
            response_data['cached_path'] = cached_info['web_path']

    return jsonify(response_data)
# Add other routes...

if __name__ == '__main__':
    # Create upload folders if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'cache'), exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)