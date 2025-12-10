# simple_server.py - Working Flask server with both pages
from flask import Flask, render_template, jsonify, request
import os
import sys
import json

app = Flask(__name__,
           static_folder='web/static',
           template_folder='web/templates')

# Create directories
os.makedirs('web/templates', exist_ok=True)
os.makedirs('web/static/css', exist_ok=True)
os.makedirs('web/static/js', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/health')
def health():
    return jsonify({
        "status": "running",
        "message": "Deepseek Web Interface is operational",
        "agents": ["basic", "enhanced", "creative"],
        "endpoints": ["/", "/chat", "/api/chat", "/api/health"]
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Simple API endpoint that returns a simulated response"""
    data = request.json
    agent_type = data.get('agent_type', 'basic')
    message = data.get('message', '')
    
    # Simulate different agent responses
    responses = {
        'basic': f"Basic Agent: I received your message: '{message}'. How can I help you further?",
        'enhanced': f"Enhanced Agent (Confident Mode): I understand you're asking about '{message}'. Here's a detailed response based on my expertise...",
        'creative': f"Creative Agent: '{message}' - Let me weave a creative response for you! 🎨✨"
    }
    
    response = responses.get(agent_type, f"I received: '{message}'")
    
    # Simulate processing time
    import time
    time.sleep(1)
    
    return jsonify({
        "response": response,
        "agent_type": agent_type,
        "timestamp": "2024-12-04T21:00:00Z",
        "status": "success"
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Deepseek Web Interface")
    print("=" * 60)
    print("Open in your browser:")
    print("1. Main page: http://localhost:5000")
    print("2. Chat interface: http://localhost:5000/chat")
    print("3. API health: http://localhost:5000/api/health")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)