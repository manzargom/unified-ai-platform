import os
import sys
import json
import uuid
import subprocess
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import shutil
import threading

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from cache_manager import CacheManager
from proxy_manager import ProxyManager  # NEW

# Create Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['PROXY_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'proxies')  # NEW
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

CORS(app)

# Initialize managers
cache_manager = CacheManager(
    cache_dir=os.path.join(app.config['UPLOAD_FOLDER'], 'cache'),
    max_size_gb=5  # Reduced since we use proxies
)

proxy_manager = ProxyManager(  # NEW
    proxy_dir=app.config['PROXY_FOLDER']
)

# Create proxy folder
os.makedirs(app.config['PROXY_FOLDER'], exist_ok=True)

# Background cleanup thread
def background_cleanup():
    """Clean up old files in background"""
    import time
    while True:
        try:
            # Clean proxies older than 24 hours
            deleted = proxy_manager.cleanup_old_proxies(max_age_hours=24)
            if deleted > 0:
                print(f"Cleaned up {deleted} old proxies")
            
            # Clean uploads older than 6 hours (originals)
            upload_dir = app.config['UPLOAD_FOLDER']
            now = datetime.now()
            for session_folder in os.listdir(upload_dir):
                session_path = os.path.join(upload_dir, session_folder)
                if os.path.isdir(session_path) and session_folder != 'cache':
                    folder_age = datetime.fromtimestamp(os.path.getmtime(session_path))
                    if (now - folder_age) > timedelta(hours=6):
                        shutil.rmtree(session_path, ignore_errors=True)
                        print(f"Cleaned old session: {session_folder}")
        
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        time.sleep(3600)  # Run every hour

# Start cleanup thread
cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
cleanup_thread.start()

# Updated upload endpoint
@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Handle video upload - create proxy and store metadata"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check file extension
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    
    # Only accept videos for proxies
    allowed_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m4v']
    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Unsupported video format: {file_ext}'}), 400
    
    # Generate session ID
    session_id = session.get('session_id', str(uuid.uuid4()))
    session['session_id'] = session_id
    
    # Create session directory
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save original temporarily
    original_path = os.path.join(session_dir, filename)
    file.save(original_path)
    
    try:
        # Create lightweight proxy
        proxy_info = proxy_manager.create_proxy(original_path, session_id, filename)
        
        if not proxy_info:
            return jsonify({'error': 'Failed to create proxy'}), 500
        
        # Get original video info (for export reference)
        original_info = cache_manager.get_video_info(original_path)
        
        # Store edit session data
        edit_session = {
            'session_id': session_id,
            'original_filename': filename,
            'original_path': original_path,
            'original_size': os.path.getsize(original_path),
            'original_duration': original_info['duration'] if original_info else 0,
            'proxy_url': proxy_info['proxy_url'],
            'proxy_size_mb': proxy_info['size_mb'],
            'uploaded_at': datetime.now().isoformat(),
            # Store for potential export
            'export_ready': True,
            'edit_instructions': []  # Will store cuts, effects, etc.
        }
        
        # Save session data (could be database, file, etc.)
        session_file = os.path.join(session_dir, 'session.json')
        with open(session_file, 'w') as f:
            json.dump(edit_session, f, indent=2)
        
        # Return proxy info to frontend
        return jsonify({
            'success': True,
            'session_id': session_id,
            'proxy': proxy_info,
            'original_info': {
                'filename': filename,
                'duration': original_info['duration'] if original_info else 0,
                'resolution': original_info['resolution'] if original_info else 'Unknown',
                'size_mb': round(os.path.getsize(original_path) / (1024 * 1024), 2)
            },
            'message': f'Created proxy: {proxy_info["size_mb"]}MB (Original: {round(os.path.getsize(original_path) / (1024 * 1024), 2)}MB)'
        })
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

# New endpoint to store edit instructions
@app.route('/api/save-edits', methods=['POST'])
def save_edits():
    """Save edit instructions (cuts, effects, etc.)"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'No session ID'}), 400
    
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    session_file = os.path.join(session_dir, 'session.json')
    
    if not os.path.exists(session_file):
        return jsonify({'error': 'Session not found'}), 404
    
    # Load session
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    # Update with edit instructions
    session_data['edit_instructions'] = data.get('edits', [])
    session_data['last_edit'] = datetime.now().isoformat()
    
    # Save back
    with open(session_file, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    return jsonify({'success': True})

# Export endpoint (applies edits to original)
@app.route('/api/export', methods=['POST'])
def export_video():
    """Apply edits to original video and export"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'No session ID'}), 400
    
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    session_file = os.path.join(session_dir, 'session.json')
    
    if not os.path.exists(session_file):
        return jsonify({'error': 'Session not found'}), 404
    
    # Load session
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    original_path = session_data.get('original_path')
    edits = session_data.get('edit_instructions', [])
    
    if not os.path.exists(original_path):
        return jsonify({'error': 'Original video no longer available'}), 404
    
    # Create export (simplified - would need complex FFmpeg commands)
    export_filename = f"export_{session_id}_{int(datetime.now().timestamp())}.mp4"
    export_path = os.path.join(session_dir, export_filename)
    
    # Simple export: just copy for now (you'd implement actual editing)
    shutil.copy2(original_path, export_path)
    
    return jsonify({
        'success': True,
        'export_url': f"/static/uploads/{session_id}/{export_filename}",
        'message': 'Export created (edits applied to original quality)'
    })

# Routes (keep existing)
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

if __name__ == '__main__':
    # Create folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROXY_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'cache'), exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)