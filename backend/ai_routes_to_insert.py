# ===========================================================================
# AI INTEGRATION - OLLAMA AI ROUTES
# ===========================================================================

@app.route('/ai-test')
def ai_test_page():
    """AI test page that connects to local Ollama"""
    try:
        # Use the existing template
        return render_template('ai_test.html')
    except Exception as e:
        print(f"AI template error: {e}")
        return f'''
        <html><body>
        <h1>AI Test</h1>
        <p>Template error: {e}</p>
        <p>Using simple fallback.</p>
        </body></html>
        '''

@app.route('/ai')
def ai_redirect():
    """Redirect to AI test page"""
    return redirect('/ai-test')

@app.route('/api/ai-status')
def ai_status():
    """Check AI status API"""
    import requests
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return jsonify({
                'status': 'online',
                'models': [m['name'] for m in models],
                'model_count': len(models),
                'message': 'Ollama is running and ready'
            })
        return jsonify({'status': 'error', 'message': 'Ollama not responding'})
    except Exception as e:
        return jsonify({'status': 'offline', 'message': str(e)})

print("✅ AI integration loaded")
