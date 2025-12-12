
import requests
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

class OllamaAI:
    """Ollama AI integration for video and content analysis"""
    
    def __init__(self, host: str = "localhost", port: int = 11434):
        self.base_url = f"http://{host}:{port}"
        self.models = self._fetch_models()
        self.available_models = [m["name"] for m in self.models]
        print(f"🤖 Ollama AI initialized. Models: {self.available_models}")
    
    def _fetch_models(self) -> List[Dict]:
        """Fetch available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get("models", [])
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
        return []
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        return len(self.models) > 0
    
    def generate(
        self,
        model: str = "mistral",
        prompt: str = "",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using Ollama
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Ollama not running. Start with: ollama serve",
                "model": model
            }
        
        if model not in self.available_models:
            model = self.available_models[0] if self.available_models else "mistral"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **kwargs
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "model": result.get("model", model),
                    "response": result.get("response", ""),
                    "total_duration": result.get("total_duration", 0),
                    "thinking_time": end_time - start_time,
                    "tokens": {
                        "prompt": result.get("prompt_eval_count", 0),
                        "response": result.get("eval_count", 0)
                    },
                    "raw": result
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama API error {response.status_code}: {response.text}",
                    "model": model
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}",
                "model": model
            }
    
    def analyze_video_content(self, description: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Analyze video content based on description/metadata
        """
        system_prompt = """You are a video content analysis expert. Analyze video content and provide:
        1. Content summary and key moments
        2. Recommended editing style (fast cuts, slow motion, etc.)
        3. Suggested background music genre
        4. Potential thumbnail ideas
        5. Target audience and engagement tips
        
        Format response with clear sections."""
        
        meta_text = ""
        if metadata:
            meta_text = f"\nMetadata: {json.dumps(metadata, indent=2)}"
        
        prompt = f"""Video Description: {description}{meta_text}

Please analyze this video content and provide creative editing suggestions:"""
        
        return self.generate(
            model="mistral",
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1500
        )
    
    def generate_video_script(self, topic: str, duration: str = "short", style: str = "educational") -> Dict[str, Any]:
        """
        Generate a video script
        """
        system_prompt = f"""You are a professional video scriptwriter. Write a {duration} {style} video script.
        Format it with:
        - Title
        - Hook/introduction
        - Main content points
        - Visual descriptions
        - Call to action
        - Suggested hashtags"""
        
        prompt = f"Create a {duration} {style} video script about: {topic}"
        
        return self.generate(
            model="mistral",
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=2000
        )
    
    def enhance_content(self, original_text: str, enhancement_type: str = "professional") -> Dict[str, Any]:
        """
        Enhance text content for videos
        """
        enhancements = {
            "professional": "Make this more professional and polished for a corporate audience.",
            "engaging": "Make this more engaging and exciting for social media.",
            "concise": "Make this more concise and to the point.",
            "detailed": "Add more detail and depth to this content.",
            "clickbait": "Make this more clickbaity and attention-grabbing for YouTube."
        }
        
        instruction = enhancements.get(enhancement_type, "Improve this text.")
        
        prompt = f"{instruction}\n\nOriginal text: {original_text}\n\nEnhanced version:"
        
        return self.generate(
            model="mistral",
            prompt=prompt,
            system_prompt="You are a content enhancement expert.",
            temperature=0.5,
            max_tokens=1500
        )
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get AI system status"""
        return {
            "status": "active" if self.is_available() else "inactive",
            "models": self.available_models,
            "default_model": "mistral",
            "total_models": len(self.available_models),
            "ollama_url": self.base_url,
            "timestamp": datetime.now().isoformat(),
            "platform": "Creator's Playground Video Platform"
        }

# Global instance
ai_engine = OllamaAI()
EOF

# Create routes/ai_routes.py
cat > routes/ai_routes.py << 'EOF'
"""
AI Routes for Creator's Playground Video Platform
Adds AI capabilities to video processing
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
        },
        "platform": "Creator's Playground"
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

@ai_bp.route('/analyze-video', methods=['POST'])
def analyze_video():
    """Analyze video content with AI"""
    data = request.json
    
    if not data or 'description' not in data:
        return jsonify({"error": "No description provided"}), 400
    
    result = ai_engine.analyze_video_content(
        description=data['description'],
        metadata=data.get('metadata', {})
    )
    
    return jsonify(result)

@ai_bp.route('/generate-script', methods=['POST'])
def generate_script():
    """Generate video script with AI"""
    data = request.json
    
    if not data or 'topic' not in data:
        return jsonify({"error": "No topic provided"}), 400
    
    result = ai_engine.generate_video_script(
        topic=data['topic'],
        duration=data.get('duration', 'short'),
        style=data.get('style', 'educational')
    )
    
    return jsonify(result)

@ai_bp.route('/enhance-content', methods=['POST'])
def enhance_content():
    """Enhance text content with AI"""
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    result = ai_engine.enhance_content(
        original_text=data['text'],
        enhancement_type=data.get('type', 'professional')
    )
    
    return jsonify(result)

@ai_bp.route('/playground', methods=['GET'])
def ai_playground():
    """AI Playground web interface"""
    return render_template('ai_playground.html', 
                         ai_status=ai_engine.get_ai_status(),
                         title="AI Playground - Creator's Playground")

@ai_bp.route('/video-ideas', methods=['POST'])
def video_ideas():
    """Generate video ideas based on theme"""
    data = request.json
    
    if not data or 'theme' not in data:
        return jsonify({"error": "No theme provided"}), 400
    
    theme = data['theme']
    count = data.get('count', 5)
    
    prompt = f"""Generate {count} creative video ideas based on the theme: "{theme}"
    
    For each idea, provide:
    1. Title
    2. Short description
    3. Target audience
    4. Estimated length
    5. Key visual elements
    
    Format as a numbered list."""
    
    result = ai_engine.generate(
        model="mistral",
        prompt=prompt,
        system_prompt="You are a creative video producer.",
        temperature=0.8,
        max_tokens=1500
    )
    
    return jsonify(result)
EOF
