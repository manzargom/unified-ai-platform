#!/usr/bin/env python3
# Deepseek Agent Framework - Main Entry Point
# Location: C:\LM Studio\AI_Agent_Framework

import sys
import os

def show_menu():
    print('=' * 60)
    print('DEEPSEEK AGENT FRAMEWORK')
    print('Location: C:\\LM Studio\\AI_Agent_Framework')
    print('=' * 60)
    print()
    print('Select Agent Type:')
    print('1. Basic Agent (Standard responses)')
    print('2. Enhanced Agent (Confident, expert mode)')
    print('3. Test LM Studio Connection')
    print('4. Exit')
    print('=' * 60)

def test_connection():
    import requests
    print('')
    print('Testing LM Studio connection...')
    try:
        response = requests.get('http://localhost:1234/v1/models', timeout=5)
        if response.status_code == 200:
            models = response.json().get('data', [])
            print('Connected to LM Studio!')
            model_names = [m['id'] for m in models]
            print(f'Available models: {model_names}')
            return True
        else:
            print(f'HTTP Error: {response.status_code}')
            return False
    except Exception as e:
        print(f'Connection failed: {e}')
        print('')
        print('Make sure:')
        print('1. LM Studio is running')
        print('2. Deepseek model is loaded')
        print('3. Local Server is started (port 1234)')
        return False

def main():
    show_menu()
    
    try:
        choice = input('Enter choice (1-4): ').strip()
        
        if choice == '1':
            from src.agents.deepseek_agent import DeepseekAgent
            agent = DeepseekAgent()
            print('')
            print('Starting Basic Agent...')
            agent.interactive_chat()
            main()
            
        elif choice == '2':
            try:
                from src.agents.enhanced_agent import EnhancedDeepseekAgent
                agent = EnhancedDeepseekAgent()
                print('')
                print('Starting Enhanced Agent (Expert Mode)...')
                agent.interactive_chat()
                main()
            except ImportError as e:
                print(f'Enhanced agent error: {e}')
                print('Using basic agent instead...')
                from src.agents.deepseek_agent import DeepseekAgent
                agent = DeepseekAgent()
                agent.interactive_chat()
                main()
                
        elif choice == '3':
            test_connection()
            input('Press Enter to return to menu...')
            main()
            
        elif choice == '4':
            print('Goodbye!')
            sys.exit(0)
            
        else:
            print('Invalid choice. Please try again.')
            main()
            
    except KeyboardInterrupt:
        print('')
        print('Framework stopped by user.')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        input('Press Enter to continue...')
        main()

if __name__ == '__main__':
    main()
