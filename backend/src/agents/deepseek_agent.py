# deepseek_agent.py
import requests
import json
import time

class DeepseekAgent:
    def __init__(self, model="deepseek-coder-6.7b-coder", api_base="http://localhost:1234/v1"):
        self.model = model
        self.api_base = api_base
        self.conversation = []
        
# Basic system prompt
        self.system_prompt = """You are Deepseek Coder - BASIC mode. Provide:
- Concise, accurate answers
- Direct code solutions
- Minimal explanation unless asked
- Focus on correctness and efficiency
Example style: "Here's the function: [code]. It works by: [brief explanation].""""
        
        # Add system prompt to conversation
        self.conversation.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        # System prompt
        self.conversation.append({
            "role": "system",
            "content": """You are Deepseek Coder 6.7B, running locally via LM Studio.
            You are a helpful, accurate, and concise programming assistant.
            Format code properly and be honest about your capabilities."""
        })
    
    def send_message(self, user_message):
        """Send message to LM Studio and get response"""
        self.conversation.append({"role": "user", "content": user_message})
        
        payload = {
            "model": self.model,
            "messages": self.conversation,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_reply = result["choices"][0]["message"]["content"]
                self.conversation.append({"role": "assistant", "content": assistant_reply})
                return assistant_reply
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_history(self):
        """Clear conversation but keep system prompt"""
        self.conversation = [self.conversation[0]] if self.conversation else []
    
    def interactive_chat(self):
        """Start interactive chat with command processing"""
        print("="*60)
        print("Deepseek Coder 6.7B (via LM Studio)")
        print("="*60)
        print("COMMANDS (processed locally, not sent to AI):")
        print("  'exit'     - Exit chat")
        print("  'clear'    - Clear conversation history")
        print("  'history'  - Show conversation")
        print("  'model X'  - Change model to X")
        print("-"*60)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                # === LOCAL COMMAND PROCESSING ===
                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    return  # Exit the function
                
                elif user_input.lower() == 'clear':
                    self.clear_history()
                    print("✓ History cleared. (This was processed locally)")
                    continue  # Don't send to AI
                
                elif user_input.lower() == 'history':
                    print("\n=== Conversation History ===")
                    for i, msg in enumerate(self.conversation):
                        role = msg["role"]
                        content_preview = msg["content"][:100].replace('\n', ' ')
                        print(f"[{i}] {role.upper()}: {content_preview}...")
                    print("="*35)
                    continue  # Don't send to AI
                
                elif user_input.lower().startswith('model '):
                    new_model = user_input[6:].strip()
                    self.model = new_model
                    print(f"✓ Model changed to: {new_model} (local change)")
                    continue  # Don't send to AI
                # === END COMMANDS ===
                
                if not user_input:
                    continue
                
                print("Thinking...", end="", flush=True)
                start = time.time()
                response = self.send_message(user_input)
                elapsed = time.time() - start
                print(f"\rAssistant ({elapsed:.1f}s): {response}")
                
            except KeyboardInterrupt:
                print("\n\nChat ended.")
                return
            except Exception as e:
                print(f"\nError: {e}")

if __name__ == "__main__":
    agent = DeepseekAgent()
    agent.interactive_chat()
