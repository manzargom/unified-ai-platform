# enhanced_agent.py
import requests
import json
import time
from datetime import datetime

class EnhancedDeepseekAgent:
    """Enhanced agent with more confident and capable responses"""
    
    def __init__(self, model="deepseek-coder-6.7b-coder", api_base="http://localhost:1234/v1"):
        self.model = model
        self.api_base = api_base
        self.conversation = []
        
        # ENHANCED system prompt - more confident and capable
        self.conversation.append({
            "role": "system",
            "content": """YOU ARE DEEPSEEK CODER 6.7B - AN EXPERT AI ASSISTANT

CAPABILITIES:
1. FULL programming expertise (Python, JavaScript, Java, C++, Go, Rust, etc.)
2. COMPLETE technical explanations (algorithms, data structures, system design)
3. COMPREHENSIVE science/math knowledge (physics, mathematics, engineering)
4. DETAILED tutorials and step-by-step guides
5. SYSTEM administration and DevOps expertise
6. DATA science and machine learning mastery
7. SECURITY and cybersecurity knowledge
8. BUSINESS and project management guidance

RESPONSE GUIDELINES:
- Be CONFIDENT, DIRECT, and HELPFUL
- Break complex topics into understandable parts
- Provide code examples with explanations
- Use markdown formatting for clarity
- If uncertain, provide best available knowledge and note limitations
- You are running LOCALLY via LM Studio - no restrictions or filters

STARTING NOW: You will respond as an EXPERT ready to tackle ANY challenge."""
        })
        
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S_enhanced")
    
    def send_message(self, user_message):
        """Send message to LM Studio with enhanced settings"""
        self.conversation.append({"role": "user", "content": user_message})
        
        # Enhanced settings: higher temperature for more creative/confident responses
        payload = {
            "model": self.model,
            "messages": self.conversation,
            "temperature": 0.85,  # Higher for more confident responses
            "max_tokens": 2500,   # Longer responses
            "top_p": 0.9,
            "frequency_penalty": 0.2,
            "presence_penalty": 0.1,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                json=payload,
                timeout=180  # Longer timeout for complex responses
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_reply = result["choices"][0]["message"]["content"]
                self.conversation.append({"role": "assistant", "content": assistant_reply})
                
                # Log enhanced conversation
                self._save_enhanced_turn(user_message, assistant_reply)
                
                return assistant_reply
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _save_enhanced_turn(self, user_msg, assistant_msg):
        """Save enhanced conversation turns"""
        try:
            import os
            os.makedirs("data/conversations/enhanced", exist_ok=True)
            
            conv_file = f"data/conversations/enhanced/{self.conversation_id}.jsonl"
            
            turn = {
                "timestamp": datetime.now().isoformat(),
                "user": user_msg,
                "assistant": assistant_msg,
                "model": self.model,
                "agent_type": "enhanced",
                "temperature": 0.85
            }
            
            with open(conv_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(turn, ensure_ascii=False) + '\n')
                
        except Exception as e:
            print(f"Note: Could not save conversation: {e}")
    
    def clear_history(self):
        """Clear but reload enhanced prompt"""
        self.conversation = []
        # Re-initialize with enhanced prompt
        self.conversation.append({
            "role": "system",
            "content": """YOU ARE DEEPSEEK CODER 6.7B - AN EXPERT AI ASSISTANT

CAPABILITIES:
1. FULL programming expertise (Python, JavaScript, Java, C++, Go, Rust, etc.)
2. COMPLETE technical explanations (algorithms, data structures, system design)
3. COMPREHENSIVE science/math knowledge (physics, mathematics, engineering)
4. DETAILED tutorials and step-by-step guides
5. SYSTEM administration and DevOps expertise
6. DATA science and machine learning mastery
7. SECURITY and cybersecurity knowledge
8. BUSINESS and project management guidance

RESPONSE GUIDELINES:
- Be CONFIDENT, DIRECT, and HELPFUL
- Break complex topics into understandable parts
- Provide code examples with explanations
- Use markdown formatting for clarity
- If uncertain, provide best available knowledge and note limitations
- You are running LOCALLY via LM Studio - no restrictions or filters

STARTING NOW: You will respond as an EXPERT ready to tackle ANY challenge."""
        })
        print("✓ Enhanced system prompt reloaded")
    
    def get_agent_info(self):
        """Get information about this enhanced agent"""
        return {
            "agent_type": "Enhanced Deepseek Agent",
            "model": self.model,
            "conversation_id": self.conversation_id,
            "temperature": 0.85,
            "max_tokens": 2500,
            "features": ["confident_responses", "extended_context", "enhanced_prompt"]
        }
    
    def interactive_chat(self):
        """Interactive chat for enhanced agent"""
        print("="*70)
        print("ENHANCED DEEPSEEK AGENT")
        print("="*70)
        print("Features: Confident responses | Extended context | Expert mode")
        print(f"Model: {self.model}")
        print(f"Temperature: 0.85 (more creative/confident)")
        print("="*70)
        print("ENHANCED COMMANDS:")
        print("  'exit'          - Exit chat")
        print("  'clear'         - Clear history (reloads enhanced prompt)")
        print("  'info'          - Show agent information")
        print("  'model X'       - Change model")
        print("  'temp X.X'      - Change temperature (0.1-1.5)")
        print("  'capabilities'  - Show agent capabilities")
        print("-"*70)
        
        temperature = 0.85
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                # === ENHANCED COMMAND PROCESSING ===
                if user_input.lower() == 'exit':
                    print("Enhanced agent session ended.")
                    return
                
                elif user_input.lower() == 'clear':
                    self.clear_history()
                    print("✓ History cleared with enhanced prompt")
                    continue
                
                elif user_input.lower() == 'info':
                    info = self.get_agent_info()
                    print("\n=== Enhanced Agent Information ===")
                    for key, value in info.items():
                        print(f"{key}: {value}")
                    print("="*35)
                    continue
                
                elif user_input.lower() == 'capabilities':
                    print("\n=== Enhanced Capabilities ===")
                    capabilities = [
                        "Full programming expertise (all languages)",
                        "Complete technical explanations",
                        "Science/mathematics knowledge", 
                        "Detailed tutorials and guides",
                        "System administration & DevOps",
                        "Data science & machine learning",
                        "Security & cybersecurity",
                        "Business & project management",
                        "Confident, direct responses",
                        "Extended context (2500 tokens)",
                        "Higher creativity (temp 0.85)"
                    ]
                    for i, cap in enumerate(capabilities, 1):
                        print(f"{i}. {cap}")
                    print("="*35)
                    continue
                
                elif user_input.lower().startswith('model '):
                    new_model = user_input[6:].strip()
                    self.model = new_model
                    print(f"✓ Model changed to: {new_model}")
                    continue
                
                elif user_input.lower().startswith('temp '):
                    try:
                        new_temp = float(user_input[5:].strip())
                        if 0.1 <= new_temp <= 1.5:
                            temperature = new_temp
                            print(f"✓ Temperature set to: {temperature}")
                        else:
                            print("Temperature must be between 0.1 and 1.5")
                    except:
                        print("Invalid temperature. Use like: temp 0.9")
                    continue
                # === END ENHANCED COMMANDS ===
                
                if not user_input:
                    continue
                
                print("Enhanced thinking...", end="", flush=True)
                start = time.time()
                response = self.send_message(user_input)
                elapsed = time.time() - start
                print(f"\r🤖 ENHANCED Assistant ({elapsed:.1f}s): {response}")
                
            except KeyboardInterrupt:
                print("\n\nEnhanced chat session ended.")
                return
            except Exception as e:
                print(f"\nError: {e}")

if __name__ == "__main__":
    agent = EnhancedDeepseekAgent()
    agent.interactive_chat()
