# test_creative.py
import sys
sys.path.append('src/agents')

from creative_agent import CreativeAgent

print("🧪 Testing Creative Agent")
print("=" * 50)

try:
    # Create agent
    agent = CreativeAgent()
    print(f"✅ Agent created")
    print(f"   Model: {agent.model}")
    print(f"   Has system_prompt: {hasattr(agent, 'system_prompt')}")
    
    if hasattr(agent, 'system_prompt'):
        print(f"   Prompt preview: {agent.system_prompt[:80]}...")
    
    # Test message
    print("\n📝 Sending test message...")
    test_message = "Help me write a mystery novel about family secrets in a haunted mansion"
    response = agent.send_message(test_message)
    
    print(f"\n📤 Response (first 300 chars):")
    print("-" * 50)
    print(response[:300] if response else "No response")
    print("-" * 50)
    
    if response and 'Error' not in response:
        print("✅ SUCCESS! Agent is working creatively!")
    else:
        print("❌ Issue with response")
        
except Exception as e:
    print(f"❌ Error: {type(e).__name__}")
    print(f"Details: {e}")