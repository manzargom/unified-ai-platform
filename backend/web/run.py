#!/usr/bin/env python3
"""
Unified Deepseek Web Interface Server
Combines all functionality into one server
Location: C:\LM Studio\AI_Agent_Framework\web
"""
import os
import sys
import uuid
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Add src to path to try importing agents
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

# Create app
app = Flask(__name__, 
           static_folder='app/static',
           template_folder='templates')
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
        'system_prompt': 'You are a helpful AI assistant. Provide clear, concise, and accurate responses.',
        'temperature': 0.7,
        'max_tokens': 2000,
        'icon': 'fas fa-comment'
    },
    'enhanced': {
        'name': 'Enhanced Agent',
        'description': 'Detailed and thorough responses with examples',
        'system_prompt': 'You are an enhanced AI assistant. Provide detailed, thorough responses with examples and explanations.',
        'temperature': 0.5,
        'max_tokens': 3000,
        'icon': 'fas fa-bolt'
    },
    'creative': {
        'name': 'Creative Agent',
        'description': 'Creative and imaginative responses',
        'system_prompt': 'You are a creative AI assistant. Be imaginative, engaging, and provide creative solutions.',
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
                print(f"Created {agent_type} agent instance for session {session_id[:8]}")
            except Exception as e:
                print(f"Failed to create {agent_type} agent: {e}")
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
                    # Some agents might need special handling
                    return f"[Real Agent] Received: {message}"
            except Exception as e:
                print(f"Agent error: {e}")
                return f"Agent error: {str(e)[:100]}..."
        
        # Simulated response
        config = AGENT_CONFIGS.get(self.agent_type, AGENT_CONFIGS['basic'])
        
        if self.agent_type == 'basic':
            return f"Basic Agent: I received your message: '{message}'. How can I assist you further?"
        elif self.agent_type == 'enhanced':
            return f"""Enhanced Agent Analysis:

Your query: "{message}"

As an enhanced AI assistant, I would provide:
1. Detailed explanation
2. Multiple perspectives
3. Practical examples
4. Related considerations
5. Best practices

What specific aspect would you like me to elaborate on?"""
        elif self.agent_type == 'creative':
            return f"""Creative Agent Response 🌟

"{message}" - what an interesting prompt!

In creative mode, I could:
• Create a story from this prompt
• Develop a character concept
• Build a fictional world
• Write a poem or creative piece

The canvas is blank, and the brush is in your hands! 🎨"""
        else:
            return f"I received: '{message}'. How can I help?"
    
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

# Routes
@app.route('/')
def index():
    """Serve main interface"""
    return render_template('index.html')

@app.route('/test')
def test():
    """Test page"""
    return "Server is running!"

@app.route('/debug')
def debug():
    """Debug information"""
    cleanup_sessions()
    return jsonify({
        'sessions': len(sessions),
        'session_ids': list(sessions.keys()),
        'agent_configs': list(AGENT_CONFIGS.keys()),
        'agents_loaded': {k: v is not None for k, v in AGENTS.items()},
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    cleanup_sessions()
    return jsonify({
        'status': 'running',
        'message': 'Deepseek Web Interface is operational',
        'available_agents': list(AGENT_CONFIGS.keys()),
        'active_sessions': len(sessions),
        'real_agents_loaded': {k: v is not None for k, v in AGENTS.items()},
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
        
        # Get response
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
        return jsonify({
            'error': str(e),
            'response': f"Error processing your message. Please try again.",
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
def test_lm():
    """Test LM Studio connection"""
    try:
        import requests
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get("data", [])
            return jsonify({
                'connected': True,
                'message': 'Connected to LM Studio',
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

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('app/static', path)

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('app/static/css', exist_ok=True)
    os.makedirs('app/static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 60)
    print("🤖 Deepseek Web Interface - Unified Edition")
    print("=" * 60)
    print(f"Location: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Available agents: {list(AGENT_CONFIGS.keys())}")
    
    # Show agent loading status
    for agent_type, agent_class in AGENTS.items():
        status = "✓ Loaded" if agent_class is not None else "✗ Not available"
        print(f"  {agent_type}: {status}")
    
    print("\nOpen in your browser:")
    print("  • Main interface: http://localhost:5000")
    print("  • API health:     http://localhost:5000/api/health")
    print("  • Debug info:     http://localhost:5000/debug")
    print("  • Test LM Studio: http://localhost:5000/api/test-lm")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)