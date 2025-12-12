# /home/anon/unified-ai-platform/backend/routes/ai_routes.py
"""
AI Routes for Creator's Playground
Adds AI capabilities to existing platform
"""

from flask import Blueprint, request, jsonify, render_template
from utils.ai_integration import ai_engine

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/status', methods=['GET'])
def ai_status():
    """Check AI status"""
    return jsonify(ai_engine.get_ai_status())

@ai_bp.route('/models', methods=['GET'])
def list_models():
    """List available AI models"""
    return jsonify({
        "available_models": ai_engine.available_models,
        "recommended": {
            "text": "mistral",
            "code": "llama3.2",
            "vision": "llava"
        }
    })

@ai_bp.route('/generate', methods=['POST'])
def generate_text():
    """Generate text with AI"""
    data = request.json
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400
    
    result = ai_engine.generate(
        model=data.get('model', 'mistral'),
        prompt=data['prompt'],
        system_prompt=data.get('system_prompt'),
        temperature=float(data.get('temperature', 0.7)),
        max_tokens=int(data.get('max_tokens', 1000))
    )
    
    return jsonify(result)

@ai_bp.route('/enhance-agent', methods=['POST'])
def enhance_agent():
    """Enhance agent responses with AI"""
    data = request.json
    
    if not data or 'agent' not in data or 'response' not in data:
        return jsonify({"error": "Missing agent or response"}), 400
    
    enhanced = ai_engine.enhance_agent_response(
        agent_name=data['agent'],
        original_response=data['response'],
        context=data.get('context', '')
    )
    
    return jsonify({
        "success": True,
        "agent": data['agent'],
        "original_response": data['response'],
        "enhanced_response": enhanced,
        "model": "mistral"
    })

@ai_bp.route('/analyze-story', methods=['POST'])
def analyze_story():
    """Analyze story with AI"""
    data = request.json
    
    if not data or 'story' not in data:
        return jsonify({"error": "No story provided"}), 400
    
    result = ai_engine.analyze_story(
        story_text=data['story'],
        model=data.get('model', 'mistral')
    )
    
    return jsonify(result)

@ai_bp.route('/playground', methods=['GET'])
def ai_playground():
    """AI Playground web interface"""
    return render_template('ai_playground.html', 
                         ai_status=ai_engine.get_ai_status())

@ai_bp.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint for conversational AI"""
    data = request.json
    
    if not data or 'messages' not in data:
        return jsonify({"error": "No messages provided"}), 400
    
    result = ai_engine.chat_with_context(
        model=data.get('model', 'mistral'),
        messages=data['messages'],
        temperature=float(data.get('temperature', 0.7))
    )
    
    return jsonify(result)