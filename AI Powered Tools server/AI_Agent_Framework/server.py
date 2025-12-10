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

# ========================
# AGENTS INTEGRATION
# ========================
try:
    from skipper import Skipper
    from kowalski import Kowalski
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Agents not available - {e}")
    AGENTS_AVAILABLE = False

# ========================
# PROJECT MANAGEMENT
# ========================
class ProjectManager:
    @staticmethod
    def get_projects_count():
        if not os.path.exists('projects'):
            return 0
        count = len([d for d in os.listdir('projects') 
                    if os.path.isdir(os.path.join('projects', d))])
        return count
    
    @staticmethod
    def list_projects():
        projects = []
        if os.path.exists('projects'):
            for project_id in os.listdir('projects'):
                project_path = os.path.join('projects', project_id)
                if os.path.isdir(project_path):
                    project_file = os.path.join(project_path, 'project.json')
                    if os.path.exists(project_file):
                        try:
                            with open(project_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            projects.append({
                                'id': project_id,
                                'name': data.get('project', {}).get('name', project_id),
                                'created': data.get('project', {}).get('created', ''),
                                'characters': len(data.get('characters', [])),
                                'scenes': len(data.get('scenes', []))
                            })
                        except:
                            projects.append({
                                'id': project_id,
                                'name': project_id,
                                'created': '',
                                'characters': 0,
                                'scenes': 0
                            })
        return projects
    
    @staticmethod
    def create_project(name, author="", description=""):
        if not name:
            return None, "Project name is required"
        
        project_id = name.lower().replace(" ", "_")
        project_path = os.path.join('projects', project_id)
        
        # Check if exists
        if os.path.exists(project_path):
            counter = 1
            while os.path.exists(f"{project_path}_{counter}"):
                counter += 1
            project_path = f"{project_path}_{counter}"
            project_id = f"{project_id}_{counter}"
        
        # Create folder structure
        folders = [
            'characters',
            'scenes',
            'assets/backgrounds',
            'assets/characters',
            'assets/ui',
            'exports'
        ]
        
        for folder in folders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        # Create project.json
        project_data = {
            'project': {
                'id': project_id,
                'name': name,
                'author': author,
                'description': description,
                'created': datetime.now().isoformat(),
                'version': '1.0.0'
            },
            'characters': [],
            'scenes': [],
            'assets': {
                'backgrounds': [],
                'characters': [],
                'ui': []
            }
        }
        
        try:
            with open(os.path.join(project_path, 'project.json'), 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            # Create basic Ren'Py script
            script_content = f'''# {name}
# Created with Creator's Playground
# Author: {author}
# Date: {datetime.now().strftime('%Y-%m-%d')}

define config.name = "{name}"
define config.version = "1.0"

# Screen size
define config.screen_width = 1920
define config.screen_height = 1080

# The game starts here
label start:
    
    "Welcome to {name}!"
    
    "This is the beginning of your story..."
    
    return
'''
            
            with open(os.path.join(project_path, 'script.rpy'), 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            return project_id, f"Project '{name}' created successfully!"
            
        except Exception as e:
            return None, f"Error creating project: {str(e)}"

# ========================
# AGENT MANAGER
# ========================
class AgentManager:
    def __init__(self):
        if AGENTS_AVAILABLE:
            self.skipper = Skipper()
            self.kowalski = Kowalski(self.skipper)
            print("✅ Agents loaded: Skipper & Kowalski")
        else:
            self.skipper = None
            self.kowalski = None
            print("⚠️ Agents not available - running in limited mode")
    
    def get_agents_status(self):
        if not AGENTS_AVAILABLE:
            return {
                'skipper': {'status': 'unavailable', 'agent': 'SKIPPER', 'operation': 'OFFLINE'},
                'kowalski': {'status': 'unavailable', 'agent': 'KOWALSKI'}
            }
        
        skipper_status = self.skipper.get_status() if self.skipper else {'status': 'offline'}
        return {
            'skipper': skipper_status,
            'kowalski': {'status': 'ready', 'agent': 'KOWALSKI'}
        }
    
    def analyze_story(self, prompt):
        if not self.kowalski:
            return {
                'success': False,
                'error': 'Kowalski agent not available',
                'message': 'Please install agents first'
            }
        
        try:
            analysis = self.kowalski.analyze_story_request(prompt)
            return {
                'success': True,
                'analysis': analysis,
                'message': f"Analysis complete: {analysis['genre']} genre"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Analysis failed'
            }
    
    def search_assets(self, query, category='backgrounds', limit=3):
        if not self.skipper:
            return {
                'success': False,
                'error': 'Skipper agent not available',
                'message': 'Please install agents first'
            }
        
        try:
            results = self.skipper.execute_search(query, category, limit)
            return {
                'success': True,
                'results': results,
                'count': len(results),
                'message': f"Found {len(results)} assets"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Search failed'
            }
    
    def get_assets_for_story(self, prompt, project_folder=''):
        if not self.kowalski or not self.skipper:
            return {
                'success': False,
                'error': 'Agents not available',
                'message': 'Please install agents first'
            }
        
        try:
            # Analyze the prompt
            analysis = self.kowalski.analyze_story_request(prompt)
            
            # Create retrieval plan
            plan = self.kowalski.create_asset_retrieval_plan(analysis, project_folder)
            
            # Execute plan
            assets = self.kowalski.coordinate_with_skipper(plan)
            
            return {
                'success': True,
                'analysis': analysis,
                'plan': plan,
                'assets': assets,
                'message': f"Retrieved {len(assets)} assets for your story"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': "Failed to retrieve assets"
            }

# Initialize managers
project_manager = ProjectManager()
agent_manager = AgentManager()

# ========================
# FLASK ROUTES
# ========================

# ----- STATIC PAGES -----
@app.route('/')
def landing_page():
    """Serve the landing page"""
    return send_from_directory('.', 'index.html')

@app.route('/creator')
def creator_tool():
    """Serve the Creator's Tool page"""
    return send_from_directory('.', 'creator.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

# ----- HEALTH & STATUS -----
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'server': "Creator's Playground",
        'version': '2.0.0',
        'time': datetime.now().strftime('%H:%M:%S'),
        'agents_available': AGENTS_AVAILABLE,
        'projects_count': project_manager.get_projects_count()
    })

@app.route('/api/stats', methods=['GET'])
def system_stats():
    """Get system statistics"""
    projects = project_manager.list_projects()
    stats = {
        'projects': len(projects),
        'characters': sum(p['characters'] for p in projects),
        'scenes': sum(p['scenes'] for p in projects),
        'agents_available': AGENTS_AVAILABLE,
        'system': 'Creator\'s Playground v2.0'
    }
    return jsonify(stats)

# ----- PROJECT MANAGEMENT -----
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get list of all projects"""
    projects = project_manager.list_projects()
    return jsonify({
        'success': True,
        'projects': projects,
        'count': len(projects)
    })

@app.route('/api/projects/create', methods=['POST'])
def create_project_api():
    """Create a new project"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        name = data.get('name', '').strip()
        author = data.get('author', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Project name is required'})
        
        project_id, message = project_manager.create_project(name, author, description)
        
        if project_id:
            return jsonify({
                'success': True,
                'project_id': project_id,
                'message': message
            })
        else:
            return jsonify({'success': False, 'error': message})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get details of a specific project"""
    project_path = os.path.join('projects', project_id)
    project_file = os.path.join(project_path, 'project.json')
    
    if not os.path.exists(project_file):
        return jsonify({'success': False, 'error': 'Project not found'})
    
    try:
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Count assets
        character_folders = os.listdir(os.path.join(project_path, 'characters')) if os.path.exists(os.path.join(project_path, 'characters')) else []
        scene_folders = os.listdir(os.path.join(project_path, 'scenes')) if os.path.exists(os.path.join(project_path, 'scenes')) else []
        
        return jsonify({
            'success': True,
            'project': project_data,
            'character_count': len(character_folders),
            'scene_count': len(scene_folders),
            'path': project_path
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ----- AGENTS API -----
@app.route('/api/agents/status', methods=['GET'])
def get_agent_status():
    """Get status of all agents"""
    status = agent_manager.get_agents_status()
    return jsonify({
        'success': True,
        'agents': status,
        'available': AGENTS_AVAILABLE,
        'message': 'Agents operational' if AGENTS_AVAILABLE else 'Agents unavailable'
    })

@app.route('/api/agents/analyze', methods=['POST'])
def analyze_story():
    """Analyze a story prompt"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'})
        
        result = agent_manager.analyze_story(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/agents/search', methods=['POST'])
def search_assets():
    """Search for assets"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        category = data.get('category', 'backgrounds')
        limit = data.get('limit', 3)
        
        if not query:
            return jsonify({'success': False, 'error': 'No query provided'})
        
        result = agent_manager.search_assets(query, category, limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/agents/get-assets', methods=['POST'])
def get_assets_for_story():
    """Get assets for a story prompt"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        project_id = data.get('project_id')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'})
        
        project_folder = ''
        if project_id:
            project_folder = os.path.join('projects', project_id)
        
        result = agent_manager.get_assets_for_story(prompt, project_folder)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ----- ASSET PREVIEW -----
@app.route('/api/assets/preview/<path:filename>')
def get_asset_preview(filename):
    """Serve asset preview images"""
    try:
        # Try to find the asset
        search_paths = []
        
        # Check in project assets
        if request.args.get('project_id'):
            project_id = request.args.get('project_id')
            project_path = os.path.join('projects', project_id)
            search_paths.append(os.path.join(project_path, 'assets', filename))
            search_paths.append(os.path.join(project_path, filename))
        
        # Check in general assets
        search_paths.append(os.path.join('assets', filename))
        
        for path in search_paths:
            if os.path.exists(path):
                return send_file(path, mimetype='image/png')
        
        # Return a simple placeholder
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (300, 200), color=(30, 30, 46))
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 280, 180], outline=(255, 94, 0), width=2)
        draw.text((120, 90), "Asset Preview", fill=(255, 94, 0))
        
        import io
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----- LEGACY COMPATIBILITY -----
@app.route('/api/chat', methods=['POST'])
def legacy_chat():
    """Legacy chat endpoint for compatibility"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip() if data else ''
        
        response = f"""🎮 **Welcome to Creator's Playground!**

You're using the legacy chat interface.

**New Features Available:**
1. 🛠️ **Creator's Tool** - Web-based visual novel studio
2. 🤖 **Agent Integration** - Skipper & Kowalski assistants

**Get Started:**
• Go to: http://localhost:5000/creator
• Click the robot icon for agent tools

**Agents Status:** {'✅ Available' if AGENTS_AVAILABLE else '⚠️ Not installed'}"""
        
        return jsonify({"response": response})
        
    except Exception as e:
        return jsonify({"response": f"❌ Error: {str(e)[:100]}"})

# ----- ERROR HANDLERS -----
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found", "status": 404}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "status": 500}), 500

# ========================
# START SERVER
# ========================
if __name__ == '__main__':
    print("=" * 60)
    print("🎮 CREATOR'S PLAYGROUND SERVER v2.0")
    print("=" * 60)
    
    # Create necessary directories
    required_dirs = [
        'static/css',
        'static/js',
        'static/images',
        'projects',
        'assets/backgrounds',
        'assets/characters',
        'assets/ui'
    ]
    
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Check for required files
    print("\n📁 System Check:")
    
    files_to_check = [
        ('index.html', 'Landing Page'),
        ('creator.html', 'Creator\'s Tool'),
        ('agents/skipper.py', 'Skipper Agent'),
        ('agents/kowalski.py', 'Kowalski Agent')
    ]
    
    all_ok = True
    for file, description in files_to_check:
        if os.path.exists(file):
            print(f"  ✅ {description}: Found")
        else:
            print(f"  ❌ {description}: Missing - {file}")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Some files are missing. The app may not work correctly.")
    
    print(f"\n🌐 Landing Page: http://localhost:5000")
    print(f"🛠️  Creator's Tool: http://localhost:5000/creator")
    print(f"🤖 Agents Status: {'✅ Available' if AGENTS_AVAILABLE else '⚠️ Not installed'}")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ ERROR: Port 5000 is already in use!")
            print("💡 Try: netstat -ano | findstr :5000")
            print("   Then close that program or use Task Manager")
        else:
            print(f"\n❌ ERROR: {e}")
        input("\nPress Enter to exit...")