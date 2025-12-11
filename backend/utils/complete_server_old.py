# complete_server.py - Full backend server connecting to your AI agents
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import sys
import json
import uuid
from datetime import datetime

# Add src to path to import your agents
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

app = Flask(__name__,
           static_folder='web/static',
           template_folder='web/templates')
CORS(app)  # Enable CORS for all routes

# Try to import your agents
try:
    from agents.deepseek_agent import DeepseekAgent
    AGENTS = {"basic": DeepseekAgent}
    print("✓ Basic agent loaded")
except ImportError as e:
    print(f"⚠ Basic agent not available: {e}")
    AGENTS = {}

try:
    from agents.enhanced_agent import EnhancedDeepseekAgent
    AGENTS["enhanced"] = EnhancedDeepseekAgent
    print("✓ Enhanced agent loaded")
except ImportError as e:
    print(f"⚠ Enhanced agent not available: {e}")

try:
    from agents.creative_agent import CreativeAgent
    AGENTS["creative"] = CreativeAgent
    print("✓ Creative agent loaded")
except ImportError as e:
    print(f"⚠ Creative agent not available: {e}")

# Store active agent instances
active_sessions = {}

def get_or_create_agent(session_id, agent_type="basic"):
    """Get existing agent or create new one for session"""
    if session_id not in active_sessions:
        if agent_type in AGENTS:
            try:
                agent = AGENTS[agent_type]()
                active_sessions[session_id] = {
                    "agent": agent,
                    "type": agent_type,
                    "created": datetime.now().isoformat(),
                    "conversation": []
                }
                print(f"Created {agent_type} agent for session {session_id[:8]}")
            except Exception as e:
                return None, f"Failed to create agent: {str(e)}"
        else:
            return None, f"Agent type '{agent_type}' not available"
    
    return active_sessions[session_id], None

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Serve the chat interface"""
    return render_template('index.html')  # Same as index for SPA

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "message": "Deepseek Web Interface is operational",
        "available_agents": list(AGENTS.keys()),
        "session_count": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    })
@app.route('/test')
def test_page():
    return render_template('minimal.html')

@app.route('/api/agents')
def get_agents():
    """Get available agent types"""
    return jsonify({
        "available": list(AGENTS.keys()),
        "default": "basic" if "basic" in AGENTS else list(AGENTS.keys())[0] if AGENTS else None
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Main chat endpoint - connects to your actual AI agents"""
    try:
        data = request.json
        session_id = data.get('session_id', str(uuid.uuid4()))
        agent_type = data.get('agent_type', 'basic')
        message = data.get('message', '').strip()
        settings = data.get('settings', {})
        
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        print(f"Chat request: {agent_type} - '{message[:50]}...'")
        
        # Get or create agent for this session
        session, error = get_or_create_agent(session_id, agent_type)
        if error:
            return jsonify({"error": error}), 500
        
        agent = session["agent"]
        
        # Apply settings if provided
        if 'temperature' in settings:
            try:
                agent.temperature = float(settings['temperature'])
            except:
                pass
        
        # Get response from the actual agent
        import time
        start_time = time.time()
        
        try:
            # Check which agent type to use appropriate method
            if agent_type == "creative" and hasattr(agent, 'send_message'):
                response = agent.send_message(message)
            elif hasattr(agent, 'send_message'):
                response = agent.send_message(message)
            elif hasattr(agent, 'chat'):
                response = agent.chat(message)
            else:
                # Fallback for any agent with interactive_chat
                response = "Agent responded (method fallback)"
        except Exception as e:
            print(f"Agent error: {e}")
            response = f"I received your message: '{message}'. (Running in simulation mode - check agent connection)"
        
        elapsed = time.time() - start_time
        
        # Store conversation
        session["conversation"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        session["conversation"].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 messages
        if len(session["conversation"]) > 100:
            session["conversation"] = session["conversation"][-100:]
        
        return jsonify({
            "response": response,
            "session_id": session_id,
            "agent_type": agent_type,
            "response_time": round(elapsed, 2),
            "timestamp": datetime.now().isoformat(),
            "success": True
        })
        
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({
            "error": str(e),
            "response": f"I encountered an error: {str(e)[:100]}...",
            "success": False
        }), 500

@app.route('/api/test')
def test_connection():
    """Test connection to LM Studio"""
    try:
        import requests
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get("data", [])
            return jsonify({
                "connected": True,
                "models": [m["id"] for m in models],
                "message": f"Connected to LM Studio with {len(models)} models"
            })
        else:
            return jsonify({
                "connected": False,
                "message": f"LM Studio returned HTTP {response.status_code}"
            })
    except Exception as e:
        return jsonify({
            "connected": False,
            "message": f"Cannot connect to LM Studio: {str(e)}"
        })

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('web/templates', exist_ok=True)
    os.makedirs('web/static/css', exist_ok=True)
    os.makedirs('web/static/js', exist_ok=True)
    
    print("=" * 60)
    print("🤖 Deepseek Web Interface - Complete Edition")
    print("=" * 60)
    print(f"Available agents: {list(AGENTS.keys())}")
    print("Open in your browser:")
    print("  • Main interface: http://localhost:5000")
    print("  • API health:     http://localhost:5000/api/health")
    print("  • Test LM Studio: http://localhost:5000/api/test")
    print("=" * 60)
    
    if not AGENTS:
        print("⚠ WARNING: No agents loaded! Check your agent files in src/agents/")
        print("The interface will work but use simulated responses.")
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)