
# ============================================================================
# AI INTEGRATION - ADDED FOR OLLAMA SUPPORT
# ============================================================================

# Import AI modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'routes'))
from routes.ai_routes import ai_bp

# Import AI engine for direct use in routes
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
try:
    from utils.ai_integration import ai_engine
    print("🤖 AI Engine loaded successfully")
except Exception as e:
    print(f"⚠️ AI Engine not available: {e}")
    ai_engine = None

# Register AI blueprint
app.register_blueprint(ai_bp)

# ============================================================================
# AI-ENHANCED ROUTES
# ============================================================================

@app.route('/ai-dashboard')
def ai_dashboard():
    """Main AI dashboard"""
    ai_status = ai_engine.get_ai_status() if ai_engine else {"status": "unavailable"}
    return render_template('ai_dashboard.html', ai_status=ai_status)

@app.route('/api/ai/video-analysis', methods=['POST'])
def ai_video_analysis():
    """AI-powered video analysis endpoint"""
    if not ai_engine:
        return jsonify({"error": "AI engine not available"}), 503
    
    if 'file' in request.files:
        # Handle file upload with AI analysis
        file = request.files['file']
        filename = secure_filename(file.filename)
        
        # For now, just analyze the filename/description
        # In future, can use LLaVA for actual video analysis
        description = f"Video file: {filename}"
        
        result = ai_engine.analyze_video_content(description)
        return jsonify(result)
    
    elif request.json and 'description' in request.json:
        # Analyze from description
        description = request.json['description']
        metadata = request.json.get('metadata', {})
        
        result = ai_engine.analyze_video_content(description, metadata)
        return jsonify(result)
    
    return jsonify({"error": "No video data provided"}), 400

# ============================================================================
# ENHANCED UPLOAD WITH AI ANALYSIS
# ============================================================================

@app.route('/api/upload-enhanced', methods=['POST'])
def upload_video_enhanced():
    """Upload video with AI analysis"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Original upload logic (from your existing function)
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    
    allowed_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m4v']
    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Unsupported video format: {file_ext}'}), 400
    
    session_id = session.get('session_id', str(uuid.uuid4()))
    session['session_id'] = session_id
    
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save original file
    original_path = os.path.join(session_dir, filename)
    file.save(original_path)
    
    # Create proxy (from your existing logic)
    try:
        proxy_info = proxy_manager.create_proxy(original_path, session_id)
    except Exception as e:
        return jsonify({'error': f'Proxy creation failed: {str(e)}'}), 500
    
    # AI Analysis (NEW)
    ai_analysis = None
    if ai_engine and ai_engine.is_available():
        try:
            description = f"Uploaded video: {filename}, Size: {os.path.getsize(original_path)} bytes"
            metadata = {
                "filename": filename,
                "extension": file_ext,
                "session_id": session_id,
                "proxy_created": proxy_info.get('success', False)
            }
            
            ai_analysis = ai_engine.analyze_video_content(description, metadata)
        except Exception as e:
            print(f"AI analysis failed: {e}")
    
    response_data = {
        'success': True,
        'session_id': session_id,
        'filename': filename,
        'proxy_url': proxy_info.get('proxy_url', ''),
        'proxy_info': proxy_info,
        'ai_analysis': ai_analysis if ai_analysis and ai_analysis.get('success') else None
    }
    
    return jsonify(response_data)

# ============================================================================
# MAIN ROUTE WITH AI STATUS
# ============================================================================

@app.route('/')
def index():
    """Main landing page with AI status"""
    ai_status = ai_engine.get_ai_status() if ai_engine else {"status": "unavailable"}
    
    # Get some AI-generated suggestions if available
    ai_suggestions = None
    if ai_engine and ai_engine.is_available():
        try:
            result = ai_engine.generate(
                prompt="Generate 3 creative video project ideas for a content creator",
                system_prompt="Be concise and creative",
                max_tokens=300
            )
            if result.get('success'):
                ai_suggestions = result.get('response')
        except:
            pass
    
    return render_template('landing.html', 
                         ai_status=ai_status,
                         ai_suggestions=ai_suggestions)

# ============================================================================
# AI TOOLS PAGE
# ============================================================================

@app.route('/ai-tools')
def ai_tools():
    """AI Tools page"""
    return render_template('ai_tools.html', 
                         ai_status=ai_engine.get_ai_status() if ai_engine else {"status": "unavailable"})

# ============================================
# SIMPLE AI TEST PAGE - ADDED FOR EASY TESTING
# ============================================

@app.route('/ai-test')
def ai_test_page():
    """Simple AI test page that anyone can use"""
    return render_template('ai_test.html')

@app.route('/api/ai-test')
def ai_test_api():
    """Simple AI test API endpoint"""
    import requests
    try:
        # Check if Ollama is running
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return jsonify({
                'status': 'online',
                'models': [m['name'] for m in models],
                'message': f'AI is ready with {len(models)} models'
            })
        return jsonify({'status': 'error', 'message': 'Ollama not responding'})
    except Exception as e:
        return jsonify({'status': 'offline', 'message': str(e)})

print("✅ AI Test routes added to app.py")
EOF