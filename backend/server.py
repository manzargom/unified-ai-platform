# server.py - COMPLETE VERSION WITH AGENTS INTEGRATED
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
import sys

# Add agents directory to path
sys.path.append('agents')

app = Flask(__name__)
CORS(app)

    """Direct AI playground without template system"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 AI Playground - Creator's Playground</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #1a1a2e; color: white; }
            .container { max-width: 800px; margin: 0 auto; padding: 30px; background: rgba(255,255,255,0.05); border-radius: 20px; }
            textarea { width: 100%; height: 150px; background: #2d2d44; color: white; border: 2px solid #8B5CF6; padding: 15px; }
            button { background: #8B5CF6; color: white; padding: 15px 30px; border: none; border-radius: 10px; cursor: pointer; margin: 10px 0; }
            .output { background: rgba(16,185,129,0.1); padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #10B981; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Playground</h1>
            <p>Connect to your local Ollama AI. Your models: llava, llama3.2, mistral</p>
            
            <textarea id="q" placeholder="Ask AI anything..."></textarea>
            <br>
            <button onclick="ask()">Ask Mistral AI</button>
            <button onclick="document.getElementById('q').value=''">Clear</button>
            
            <div id="answer" class="output">AI response will appear here</div>
            
            <p style="margin-top: 30px;"><a href="/" style="color: #8B5CF6;">← Back to Creator's Playground</a></p>
        </div>
        
        <script>
            function ask() {
                const q = document.getElementById('q').value;
                const ans = document.getElementById('answer');
                
                if (!q) {
                    ans.innerHTML = "Please enter a question";
                    ans.style.background = "rgba(239,68,68,0.1)";
                    ans.style.borderColor = "#EF4444";
                    return;
                }
                
                ans.innerHTML = "Thinking... (10-30 seconds)";
                ans.style.background = "rgba(245,158,11,0.1)";
                ans.style.borderColor = "#F59E0B";
                
                fetch('http://localhost:11434/api/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        model: 'mistral',
                        prompt: q,
                        stream: false
                    })
                })
                .then(r => r.json())
                .then(data => {
                    ans.innerHTML = "<strong>🤖 AI Response:</strong><br><br>" + 
                        data.response.replace(/\\n/g, '<br>');
                    ans.style.background = "rgba(16,185,129,0.1)";
                    ans.style.borderColor = "#10B981";
                })
                .catch(e => {
                    ans.innerHTML = "Error: " + e.message + "<br>Start Ollama: <code>ollama serve</code>";
                    ans.style.background = "rgba(239,68,68,0.1)";
                    ans.style.borderColor = "#EF4444";
                });
            }
            
            // Check AI status on load
            fetch('http://localhost:11434/api/tags')
                .then(r => r.json())
                .then(data => {
                    console.log('AI Models:', data.models);
                })
                .catch(e => {
                    document.getElementById('answer').innerHTML = 
                        "⚠️ Ollama not running. Start with: <code>ollama serve</code>";
                });
        </script>
    </body>
    </html>
    '''

