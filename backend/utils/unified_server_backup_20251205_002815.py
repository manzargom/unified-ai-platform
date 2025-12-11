#!/usr/bin/env python3
"""
UNIFIED DEEPSEEK WEB SERVER
Uses your existing web/static and web/templates structure
Location: C:\LM Studio\AI_Agent_Framework\
"""
import os
import sys
import uuid
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Get current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, 'web')
STATIC_DIR = os.path.join(WEB_DIR, 'static')
TEMPLATES_DIR = os.path.join(WEB_DIR, 'templates')

print(f"Base directory: {BASE_DIR}")
print(f"Web directory: {WEB_DIR}")
print(f"Static directory: {STATIC_DIR}")
print(f"Templates directory: {TEMPLATES_DIR}")

# Add src to path to try importing agents
sys.path.append(os.path.join(BASE_DIR, 'src'))

# Create app with correct paths
app = Flask(__name__, 
           static_folder=STATIC_DIR,
           template_folder=TEMPLATES_DIR)
CORS(app)

# Try to import actual agents
AGENTS = {}
try:
    from agents.deepseek_agent import DeepseekAgent
    AGENTS['basic'] = DeepseekAgent
    print("✓ Basic agent loaded")
except ImportError as e:
    print(f"⚠ Basic agent not available: {e}")
    AGENTS['basic'] = None

try:
    from agents.enhanced_agent import EnhancedDeepseekAgent
    AGENTS['enhanced'] = EnhancedDeepseekAgent
    print("✓ Enhanced agent loaded")
except ImportError as e:
    print(f"⚠ Enhanced agent not available: {e}")
    AGENTS['enhanced'] = None

try:
    from agents.creative_agent import CreativeAgent
    AGENTS['creative'] = CreativeAgent
    print("✓ Creative agent loaded")
except ImportError as e:
    print(f"⚠ Creative agent not available: {e}")
    AGENTS['creative'] = None

# Agent configurations
AGENT_CONFIGS = {
    'basic': {
        'name': 'Basic Agent',
        'description': 'Standard responses, balanced and helpful',
        'system_prompt': '''You are Deepseek Coder - BASIC mode. Provide:
- Concise, accurate answers
- Direct code solutions
- Minimal explanation unless asked
- Focus on correctness and efficiency
Example style: "Here's the function: [code]. It works by: [brief explanation]."''',
        'temperature': 0.7,
        'max_tokens': 2000,
        'icon': 'fas fa-comment'
    },
    'enhanced': {
        'name': 'Enhanced Agent',
        'description': 'Detailed and thorough responses with examples',
        'system_prompt': '''You are Deepseek Coder - ENHANCED mode. Provide:
- Detailed, thorough explanations
- Multiple approaches/solutions
- Best practices and patterns
- Edge cases and considerations
- Code examples with comments
Example style: "Approach 1: [explanation with pros/cons]. Approach 2: [alternative]."''',
        'temperature': 0.5,
        'max_tokens': 3000,
        'icon': 'fas fa-bolt'
    },
    'creative': {
        'name': 'Creative Agent',
        'description': 'Creative and imaginative responses',
        'system_prompt': '''You are Deepseek Creative - CREATIVE mode. Provide:
- Imaginative, engaging content
- Story and character development
- Worldbuilding details
- Creative problem-solving
- Collaborative brainstorming
Example style: "Let's create! Here's a concept: [idea]. We could develop it by: [suggestions]."''',
        'temperature': 0.9,
        'max_tokens': 2500,
        'icon': 'fas fa-paint-brush'
    }
}

# Session storage
sessions = {}

class ChatSession:
    """Manages a chat session"""
    def __init__(self, session_id, agent_type='basic'):
        self.session_id = session_id
        self.agent_type = agent_type
        self.messages = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.agent_instance = None
        
        # Try to create actual agent instance
        if agent_type in AGENTS and AGENTS[agent_type] is not None:
            try:
                self.agent_instance = AGENTS[agent_type]()
                print(f"✓ Created {agent_type} agent for session {session_id[:8]}")
            except Exception as e:
                print(f"✗ Failed to create {agent_type} agent: {e}")
                self.agent_instance = None
    
    def add_message(self, role, content):
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'agent_type': self.agent_type
        }
        self.messages.append(message)
        self.last_activity = datetime.now()
        
        # Keep only last 100 messages
        if len(self.messages) > 100:
            self.messages = self.messages[-100:]
        
        return message
    
    def get_response(self, message):
        """Get response from agent or simulated"""
        if self.agent_instance:
            try:
                # Try different method names
                if hasattr(self.agent_instance, 'send_message'):
                    return self.agent_instance.send_message(message)
                elif hasattr(self.agent_instance, 'chat'):
                    return self.agent_instance.chat(message)
                elif hasattr(self.agent_instance, 'interactive_chat'):
                    # Simulate interactive chat
                    return f"[{self.agent_type.title()} Agent]: I received your message: '{message}'\n(Using real agent backend)"
            except Exception as e:
                print(f"Agent error: {e}")
                return f"⚠ Agent error: {str(e)[:100]}..."
        
        # Fallback: Simulated response
        if self.agent_type == 'basic':
            return f"🤖 Basic Agent: I received: '{message}'\n\nHow can I help you today?"
        elif self.agent_type == 'enhanced':
            return f"⚡ Enhanced Agent: Analyzing: '{message}'\n\nAs an enhanced agent, I provide detailed, thorough responses with examples and practical advice."
        elif self.agent_type == 'creative':
            return f"🎨 Creative Agent: '{message}' - What an inspiring prompt!\n\nLet's create something amazing together! 🌟"
        else:
            return f"🤖 AI Assistant: I received: '{message}'. How can I assist you?"
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'agent_type': self.agent_type,
            'message_count': len(self.messages),
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'has_real_agent': self.agent_instance is not None
        }

def get_session(session_id=None, agent_type='basic'):
    """Get or create a session"""
    if session_id and session_id in sessions:
        session = sessions[session_id]
        session.last_activity = datetime.now()
        return session
    
    # Create new session
    if not session_id:
        session_id = str(uuid.uuid4())
    
    session = ChatSession(session_id, agent_type)
    sessions[session_id] = session
    return session

def cleanup_sessions():
    """Remove inactive sessions (older than 1 hour)"""
    now = datetime.now()
    to_remove = []
    
    for session_id, session in sessions.items():
        if (now - session.last_activity).seconds > 3600:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        del sessions[session_id]

# ===== ROUTES =====

@app.route('/')
def index():
    """Serve main interface"""
    print(f"📄 Serving index.html from: {TEMPLATES_DIR}")
    return render_template('index.html')

@app.route('/test')
def test_page():
    """Simple test page"""
    return "✅ Server is running!"

@app.route('/debug')
def debug_info():
    """Debug information"""
    cleanup_sessions()
    return jsonify({
        'status': 'running',
        'paths': {
            'base': BASE_DIR,
            'web': WEB_DIR,
            'static': STATIC_DIR,
            'templates': TEMPLATES_DIR
        },
        'agents': {
            'available': list(AGENT_CONFIGS.keys()),
            'loaded': {k: v is not None for k, v in AGENTS.items()}
        },
        'sessions': {
            'count': len(sessions),
            'active': list(sessions.keys())
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    cleanup_sessions()
    return jsonify({
        'status': 'healthy',
        'message': 'Deepseek Web Interface is operational',
        'version': '1.0.0',
        'available_agents': list(AGENT_CONFIGS.keys()),
        'active_sessions': len(sessions),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agents')
def get_agents():
    """Get available agents"""
    return jsonify({
        'agents': list(AGENT_CONFIGS.keys()),
        'configs': AGENT_CONFIGS,
        'real_agents_available': {k: v is not None for k, v in AGENTS.items()}
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        session_id = data.get('session_id')
        agent_type = data.get('agent_type', 'basic')
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get or create session
        session = get_session(session_id, agent_type)
        
        # Add user message
        session.add_message('user', message)
        
        # Get response with timing
        start_time = time.time()
        response = session.get_response(message)
        elapsed = time.time() - start_time
        
        # Simulate processing time if too fast
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)
            elapsed = 0.5
        
        # Add assistant response
        session.add_message('assistant', response)
        
        return jsonify({
            'response': response,
            'session_id': session.session_id,
            'agent_type': agent_type,
            'agent_name': AGENT_CONFIGS.get(agent_type, {}).get('name', 'AI Assistant'),
            'response_time': round(elapsed, 2),
            'using_real_agent': session.agent_instance is not None,
            'timestamp': datetime.now().isoformat(),
            'success': True
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'response': f"Error: {str(e)[:100]}...",
            'success': False
        }), 500

@app.route('/api/sessions')
def list_sessions():
    """List all active sessions"""
    cleanup_sessions()
    return jsonify({
        'sessions': [session.to_dict() for session in sessions.values()],
        'count': len(sessions)
    })

@app.route('/api/test-lm')
def test_lm_studio():
    """Test LM Studio connection"""
    try:
        import requests
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get("data", [])
            return jsonify({
                'connected': True,
                'message': 'Connected to LM Studio!',
                'models': [m["id"] for m in models],
                'url': 'http://localhost:1234/v1'
            })
    except Exception as e:
        pass
    
    return jsonify({
        'connected': False,
        'message': 'LM Studio not detected',
        'note': 'Make sure LM Studio is running with server on port 1234'
    })

@app.route('/api/echo', methods=['POST'])
def echo():
    """Echo endpoint for testing"""
    data = request.json
    return jsonify({
        'echo': data.get('message', 'No message'),
        'timestamp': datetime.now().isoformat()
    })

# Static file serving
@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files from web/static/"""
    return send_from_directory(STATIC_DIR, path)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found', 'path': request.path}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(STATIC_DIR, exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, 'css'), exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, 'js'), exist_ok=True)
    
    print("=" * 70)
    print("🤖 DEEPSEEK WEB INTERFACE - UNIFIED SERVER")
    print("=" * 70)
    print(f"📍 Location: {BASE_DIR}")
    print(f"📁 Using your existing structure:")
    print(f"   ├── Static files: {STATIC_DIR}")
    print(f"   ├── Templates: {TEMPLATES_DIR}")
    print(f"   └── Agents: {list(AGENTS.keys())}")
    
    print("\n📊 Agent Status:")
    for agent_type in AGENT_CONFIGS.keys():
        if agent_type in AGENTS and AGENTS[agent_type] is not None:
            print(f"   ✓ {agent_type}: REAL AGENT LOADED")
        else:
            print(f"   ⚠ {agent_type}: Simulation mode")
    
    print("\n🌐 Endpoints:")
    print("   • Main Interface:  http://localhost:5000")
    print("   • API Health:      http://localhost:5000/api/health")
    print("   • Debug Info:      http://localhost:5000/debug")
    print("   • Test LM Studio:  http://localhost:5000/api/test-lm")
    print("   • List Sessions:   http://localhost:5000/api/sessions")
    print("   • Test Echo:       POST http://localhost:5000/api/echo")
    print("\n🔄 Starting server...")
    print("=" * 70)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n💥 Server error: {e}")