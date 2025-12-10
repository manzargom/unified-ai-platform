# backend/server.py - CRASH-PROOF VERSION
import traceback

try:
    from flask import Flask, jsonify, send_from_directory
    from flask_cors import CORS
    import os
    import json
    from datetime import datetime
    
    print("✅ Flask imports successful")
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    print("\n💡 Install missing packages:")
    print("   pip install flask flask-cors")
    input("\nPress Enter to exit...")
    exit(1)

# Create app
app = Flask(__name__)
CORS(app)

# Configuration
PORT = 5051
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"📁 Base directory: {BASE_DIR}")

# Routes
@app.route('/')
def index():
    """Serve the main editor page"""
    try:
        return send_from_directory(BASE_DIR, 'index.html')
    except Exception as e:
        return f"""
        <html>
        <body style="background:#0a0a0f; color:white; padding:40px; font-family:Arial;">
            <h1>🎬 Video Editor</h1>
            <p>Server is running, but index.html not found.</p>
            <p>Error: {str(e)}</p>
            <p>Looking in: {BASE_DIR}</p>
            <p>Files in directory:</p>
            <pre>{os.listdir(BASE_DIR) if os.path.exists(BASE_DIR) else 'Directory not found'}</pre>
            <p><a href="/api/health" style="color:#ff5e00;">Check API Health</a></p>
        </body>
        </html>
        """

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'running',
        'port': PORT,
        'message': 'Server is working!'
    })

@app.route('/<path:path>')
def serve_file(path):
    """Serve any file from the base directory"""
    try:
        return send_from_directory(BASE_DIR, path)
    except:
        return jsonify({'error': 'File not found', 'path': path}), 404

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found', 'path': request.path}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🎬 VIDEO EDITOR - DEBUG SERVER")
    print("=" * 60)
    print(f"🌐 URL: http://localhost:{PORT}")
    print(f"📁 Serving from: {BASE_DIR}")
    print("=" * 60)
    
    try:
        # Check if index.html exists
        index_path = os.path.join(BASE_DIR, 'index.html')
        if os.path.exists(index_path):
            print(f"✅ Found index.html: {index_path}")
        else:
            print(f"❌ MISSING: index.html not found at {index_path}")
            print("💡 Create index.html in the video-editor folder")
        
        print("\n🚀 Starting server...")
        app.run(debug=False, port=PORT, host='0.0.0.0', use_reloader=False)
        
    except Exception as e:
        print(f"\n❌ CRASHED: {e}")
        print("\n🔧 Stack trace:")
        traceback.print_exc()
        
        print("\n💡 Common fixes:")
        print("1. Port already in use:")
        print(f"   netstat -ano | findstr :{PORT}")
        print("2. Kill process or change PORT variable")
        print("3. Check file permissions")
        
        input("\nPress Enter to exit...")