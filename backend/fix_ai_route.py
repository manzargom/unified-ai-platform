import re

with open('server.py', 'r') as f:
    content = f.read()

# Find the ai_test_page function and fix it
# We'll replace it with a simpler version that definitely works
new_ai_route = '''
@app.route('/ai-test')
def ai_test_page():
    """AI test page that connects to local Ollama"""
    try:
        # Try to use the template
        return render_template('ai_test.html')
    except Exception as e:
        # If template fails, serve a direct HTML file
        try:
            with open('templates/ai_test.html', 'r') as f:
                return f.read()
        except:
            # Ultimate fallback
            return """
            <!DOCTYPE html>
            <html>
            <head><title>AI Playground</title></head>
            <body style="font-family: Arial; margin: 40px;">
                <h1>🤖 AI Playground</h1>
                <p>Direct HTML fallback - template system not working</p>
                <p><a href="/">← Back</a></p>
            </body>
            </html>
            """

@app.route('/ai')
def ai_redirect():
    """Redirect to AI test page"""
    return redirect('/ai-test')
'''

# Find and replace the existing AI route
# Look for the pattern from @app.route('/ai-test') to the next @app.route or empty line
pattern = r'@app.route\(\'/ai-test\'\).*?(@app.route\(|if __name__)'
replacement = r'''@app.route('/ai-test')
def ai_test_page():
    """AI test page that connects to local Ollama"""
    try:
        # Try to use the template
        return render_template('ai_test.html')
    except Exception as e:
        # If template fails, serve a direct HTML file
        try:
            with open('templates/ai_test.html', 'r') as f:
                return f.read()
        except:
            # Ultimate fallback
            return """
            <!DOCTYPE html>
            <html>
            <head><title>AI Playground</title></head>
            <body style="font-family: Arial; margin: 40px;">
                <h1>🤖 AI Playground</h1>
                <p>Direct HTML fallback - template system not working</p>
                <p><a href="/">← Back</a></p>
            </body>
            </html>
            """

@app.route('/ai')
def ai_redirect():
    """Redirect to AI test page"""
    return redirect('/ai-test')

\1'''

# Do the replacement
import re
updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('server.py', 'w') as f:
    f.write(updated_content)

print("✅ Fixed AI route to handle templates properly")
