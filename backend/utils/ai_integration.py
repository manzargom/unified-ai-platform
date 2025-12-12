# /home/anon/unified-ai-platform/backend/utils/ai_integration.py
"""
AI Integration for Creator's Playground
Connects Ollama models to your existing agents
"""

import requests
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

class OllamaAI:
    """Ollama AI integration for Creator's Playground"""
    
    def __init__(self, host: str = "localhost", port: int = 11434):
        self.base_url = f"http://{host}:{port}"
        self.models = self._fetch_models()
        self.available_models = [m["name"] for m in self.models]
        print(f"🤖 Ollama AI initialized. Available models: {self.available_models}")
    
    def _fetch_models(self) -> List[Dict]:
        """Fetch available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get("models", [])
        except Exception as e:
            print(f"⚠️ Could not connect to Ollama: {e}")
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
        
        Args:
            model: Model name (mistral, llama3.2, llava)
            prompt: User prompt
            system_prompt: System instructions
            temperature: Creativity (0.0-1.0)
            max_tokens: Maximum response length
        
        Returns:
            Dict with response and metadata
        """
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
    
    def chat_with_context(
        self,
        model: str,
        messages: List[Dict],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Chat with context (multiple messages)"""
        # Convert messages to a single prompt with context
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt += f"{role.upper()}: {content}\n\n"
        
        prompt += "ASSISTANT:"
        
        return self.generate(
            model=model,
            prompt=prompt,
            temperature=temperature
        )
    
    def enhance_agent_response(
        self,
        agent_name: str,
        original_response: str,
        context: str = ""
    ) -> str:
        """
        Enhance agent responses with AI
        
        Args:
            agent_name: "kowalski" or "skipper"
            original_response: Agent's original response
            context: Additional context
        
        Returns:
            Enhanced response
        """
        if agent_name.lower() == "kowalski":
            system_prompt = """You are Kowalski, an analytical AI assistant. 
            Enhance this analysis with more detail, structure, and insights.
            Keep the analytical tone but make it more comprehensive."""
        elif agent_name.lower() == "skipper":
            system_prompt = """You are Skipper, a creative AI assistant.
            Enhance this creative response with more flair, imagination, and engaging details.
            Keep the creative and enthusiastic tone."""
        else:
            system_prompt = "Enhance this response with more detail and clarity."
        
        prompt = f"""
        Original {agent_name} response: {original_response}
        
        Context: {context}
        
        Enhanced response:"""
        
        result = self.generate(
            model="mistral",
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )
        
        if result["success"]:
            return result["response"]
        return original_response  # Fallback to original
    
    def analyze_story(self, story_text: str, model: str = "mistral") -> Dict[str, Any]:
        """Analyze story content with AI"""
        system_prompt = """You are a story analysis expert. Analyze the story and provide:
        1. Main theme and message
        2. Key characters and their roles
        3. Emotional arc and tone
        4. Visual elements that could be illustrated
        5. Recommended adaptations (game, video, comic, etc.)
        
        Format as structured analysis with bullet points."""
        
        prompt = f"Analyze this story:\n\n{story_text}"
        
        return self.generate(
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
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
            "timestamp": datetime.now().isoformat()
        }


# Global instance for easy access
ai_engine = OllamaAI()