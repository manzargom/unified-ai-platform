# web_server.py
"""
Modern Web Interface for Deepseek Agent Framework
Provides HTML/JS interface and API endpoints
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Try to import agents
AGENTS = {}
try:
    from agents.deepseek_agent import DeepseekAgent
    AGENTS["basic"] = lambda: DeepseekAgent()
    print("✓ Basic agent loaded")
except ImportError as e:
    print(f"Basic agent not available: {e}")

try:
    from agents.enhanced_agent import EnhancedDeepseekAgent
    AGENTS["enhanced"] = lambda: EnhancedDeepseekAgent()
    print("✓ Enhanced agent loaded")
except ImportError as e:
    print(f"Enhanced agent not available: {e}")

try:
    from agents.creative_agent import CreativeAgent
    AGENTS["creative"] = lambda: CreativeAgent()
    print("✓ Creative agent loaded")
except ImportError as e:
    print(f"Creative agent not available: {e}")

app = Flask(__name__, 
           static_folder='web/static',
           template_folder='web/templates')
CORS(app)

# Active agents for each session
active_agents = {}
agent_lock = threading.Lock()

def create_agent(agent_type="basic", session_id=None):
    """Create or get an agent for a session"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    with agent_lock:
        if session_id not in active_agents:
            if agent_type in AGENTS:
                try:
                    agent = AGENTS[agent_type]()
                    active_agents[session_id] = {
                        "agent": agent,
                        "type": agent_type,
                        "created": datetime.now().isoformat(),
                        "last_used": datetime.now().isoformat(),
                        "conversation": []
                    }
                    print(f"Created {agent_type} agent for session {session_id[:8]}")
                except Exception as e:
                    return None, f"Failed to create agent: {str(e)}"
            else:
                return None, f"Agent type '{agent_type}' not available"
        else:
            # Update last used time
            active_agents[session_id]["last_used"] = datetime.now().isoformat()
        
        return active_agents[session_id], None

def cleanup_old_sessions():
    """Clean up sessions older than 1 hour"""
    with agent_lock:
        now = datetime.now()
        to_remove = []
        
        for session_id, session_data in active_agents.items():
            last_used = datetime.fromisoformat(session_data["last_used"])
            if (now - last_used).seconds > 3600:  # 1 hour
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del active_agents[session_id]
            print(f"Cleaned up old session: {session_id[:8]}")

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "available_agents": list(AGENTS.keys()),
        "active_sessions": len(active_agents)
    })

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get available agent types"""
    return jsonify({
        "available": list(AGENTS.keys()),
        "default": "basic" if "basic" in AGENTS else list(AGENTS.keys())[0] if AGENTS else None
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        session_id = data.get("session_id")
        agent_type = data.get("agent_type", "basic")
        message = data.get("message", "").strip()
        settings = data.get("settings", {})
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Clean up old sessions
        cleanup_old_sessions()
        
        # Get or create agent for session
        session, error = create_agent(agent_type, session_id)
        if error:
            return jsonify({"error": error}), 500
        
        # Update agent settings if provided
        agent = session["agent"]
        if settings.get("temperature"):
            agent.temperature = float(settings["temperature"])
        if settings.get("maxTokens"):
            agent.max_tokens = int(settings["maxTokens"])
        if settings.get("model"):
            agent.model = settings["model"]
        
        # Get response from agent
        start_time = time.time()
        response = agent.send_message(message)
        elapsed = time.time() - start_time
        
        # Update conversation history
        session["conversation"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        session["conversation"].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat(),
            "response_time": round(elapsed, 2)
        })
        
        # Keep only last 50 messages
        if len(session["conversation"]) > 50:
            session["conversation"] = session["conversation"][-50:]
        
        return jsonify({
            "response": response,
            "session_id": session_id,
            "agent_type": agent_type,
            "response_time": round(elapsed, 2),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversation/<session_id>', methods=['GET'])
def get_conversation(session_id):
    """Get conversation history for a session"""
    if session_id in active_agents:
        return jsonify({
            "session_id": session_id,
            "agent_type": active_agents[session_id]["type"],
            "conversation": active_agents[session_id]["conversation"]
        })
    return jsonify({"error": "Session not found"}), 404

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all active sessions"""
    sessions = []
    for session_id, data in active_agents.items():
        sessions.append({
            "id": session_id[:8],
            "agent_type": data["type"],
            "created": data["created"],
            "last_used": data["last_used"],
            "message_count": len(data["conversation"])
        })
    return jsonify({"sessions": sessions})

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('web/static', path)

if __name__ == '__main__':
    # Create required directories
    os.makedirs("web/static", exist_ok=True)
    os.makedirs("web/templates", exist_ok=True)
    
    print("=" * 60)
    print("Deepseek Web Interface")
    print("=" * 60)
    print(f"Available agents: {list(AGENTS.keys())}")
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)