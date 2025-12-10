# agents/skipper.py - Web Asset Retriever Agent
import requests
import os
import json
from datetime import datetime
import random
from PIL import Image, ImageDraw, ImageFont

class Skipper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.operation_name = "ASSET RETRIEVAL"
        self.status = "READY"
        self.mission_log = []
        
        self.asset_dirs = {
            'backgrounds': 'assets/backgrounds',
            'characters': 'assets/characters',
            'ui': 'assets/ui',
            'music': 'assets/music',
            'sfx': 'assets/sfx'
        }
        
        for dir_path in self.asset_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        self.log("Agent Skipper online. Mission: Retrieve visual novel assets!")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.mission_log.append(log_entry)
        print(f"🐧 SKIPPER: {message}")
        return log_entry
    
    def execute_search(self, query, category='backgrounds', limit=5):
        self.status = "SEARCHING"
        self.log(f"Mission: Retrieve '{query}' assets")
        self.log(f"Category: {category}")
        self.log(f"Limit: {limit} targets")
        
        results = []
        query_lower = query.lower()
        
        target_profiles = {
            'fantasy': {
                'backgrounds': [
                    'https://placehold.co/1920x1080/1a1a2e/00b4d8/png?text=FANTASY+FOREST',
                    'https://placehold.co/1920x1080/16213e/e94560/png?text=MAGIC+CASTLE',
                    'https://placehold.co/1920x1080/0f3460/ff9a00/png?text=DRAGON+LAIR'
                ],
                'characters': [
                    'https://placehold.co/800x1200/1a1a2e/ffffff/png?text=WIZARD',
                    'https://placehold.co/800x1200/16213e/00b4d8/png?text=ELF+ARCHER',
                    'https://placehold.co/800x1200/0f3460/e94560/png?text=KNIGHT'
                ]
            },
            'sci_fi': {
                'backgrounds': [
                    'https://placehold.co/1920x1080/000033/00ccff/png?text=SPACE+STATION',
                    'https://placehold.co/1920x1080/330033/ff00ff/png?text=FUTURISTIC+CITY',
                    'https://placehold.co/1920x1080/003300/00ff00/png?text=ALIEN+PLANET'
                ],
                'characters': [
                    'https://placehold.co/800x1200/000033/ffffff/png?text=CYBER+SAMURAI',
                    'https://placehold.co/800x1200/330033/00ccff/png?text=ROBOT',
                    'https://placehold.co/800x1200/003300/ff00ff/png?text=SPACE+MERCENARY'
                ]
            },
            'romance': {
                'backgrounds': [
                    'https://placehold.co/1920x1080/660033/ff6699/png?text=ROMANTIC+SUNSET',
                    'https://placehold.co/1920x1080/330066/cc99ff/png?text=CAFE+SCENE',
                    'https://placehold.co/1920x1080/006666/00ffcc/png?text=BEACH+WALK'
                ],
                'characters': [
                    'https://placehold.co/800x1200/660033/ffffff/png?text=ROMANTIC+LEAD',
                    'https://placehold.co/800x1200/330066/ff6699/png?text=LOVE+INTEREST',
                    'https://placehold.co/800x1200/006666/cc99ff/png?text=SUPPORTING+CHAR'
                ]
            }
        }
        
        if any(word in query_lower for word in ['fantasy', 'magic', 'dragon', 'elf', 'wizard']):
            target_type = 'fantasy'
        elif any(word in query_lower for word in ['sci', 'space', 'future', 'robot', 'cyber']):
            target_type = 'sci_fi'
        elif any(word in query_lower for word in ['love', 'romance', 'cafe', 'date']):
            target_type = 'romance'
        else:
            target_type = 'fantasy'
        
        self.log(f"Target type identified: {target_type.upper()}")
        
        targets = target_profiles[target_type].get(category, [])
        
        for i, url in enumerate(targets[:limit]):
            target_id = f"TARGET_{datetime.now().strftime('%H%M%S')}_{i}"
            
            result = {
                'id': target_id,
                'query': query,
                'url': url,
                'category': category,
                'filename': f"{category}_{query.replace(' ', '_')}_{target_id}.png",
                'target_type': target_type,
                'description': f"EXTRACTED: {query} - {category}",
                'extraction_time': datetime.now().isoformat(),
                'agent': 'SKIPPER'
            }
            
            results.append(result)
            self.log(f"Target acquired: {target_id}")
        
        self.status = "TARGETS ACQUIRED"
        self.log(f"Mission successful: {len(results)} targets acquired")
        
        return results
    
    def download_asset(self, asset_info, project_folder=''):
        try:
            url = asset_info['url']
            filename = asset_info['filename']
            category = asset_info['category']
            target_id = asset_info['id']
            
            self.log(f"Downloading target: {target_id}")
            
            if project_folder:
                secure_location = os.path.join(project_folder, 'assets', category)
                os.makedirs(secure_location, exist_ok=True)
                asset_path = os.path.join(secure_location, filename)
            else:
                secure_location = self.asset_dirs.get(category, 'assets/general')
                os.makedirs(secure_location, exist_ok=True)
                asset_path = os.path.join(secure_location, filename)
            
            tactical_colors = [
                ('#1a1a2e', '#00b4d8', 'NIGHT OPS'),
                ('#16213e', '#e94560', 'COMBAT RED'),
                ('#0f3460', '#ff9a00', 'WARNING'),
                ('#2c3e50', '#ecf0f1', 'STEALTH'),
            ]
            
            bg_color, text_color, codename = random.choice(tactical_colors)
            
            if 'background' in category:
                img = Image.new('RGB', (1920, 1080), bg_color)
            else:
                img = Image.new('RGB', (800, 1200), bg_color)
            
            draw = ImageDraw.Draw(img)
            
            try:
                font_large = ImageFont.truetype("arial.ttf", 60)
                font_small = ImageFont.truetype("arial.ttf", 30)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            mission_text = f"MISSION: {asset_info['query'].upper()}\n"
            mission_text += f"TARGET: {target_id}\n"
            mission_text += f"AGENT: SKIPPER\n"
            mission_text += f"STATUS: ASSET ACQUIRED"
            
            draw.text((50, 50), mission_text, fill=text_color, font=font_small)
            
            category_text = f"[{category.upper()}]"
            draw.text((img.width//2 - 100, img.height//2), category_text, fill=text_color, font=font_large)
            
            img.save(asset_path, 'PNG')
            
            self.log(f"Asset secured at: {asset_path}")
            
            asset_info['local_path'] = asset_path
            asset_info['secure_location'] = secure_location
            asset_info['download_complete'] = datetime.now().isoformat()
            asset_info['codename'] = codename
            
            return asset_info
            
        except Exception as e:
            self.log(f"MISSION FAILED: {str(e)}")
            return None
    
    def full_mission(self, query, category='backgrounds', project_folder='', limit=3):
        self.log("=== MISSION START ===")
        self.log(f"QUERY: '{query}'")
        self.log(f"OBJECTIVE: Retrieve {limit} {category} assets")
        
        targets = self.execute_search(query, category, limit)
        
        extracted_assets = []
        for target in targets:
            extracted = self.download_asset(target, project_folder)
            if extracted:
                extracted_assets.append(extracted)
        
        if extracted_assets:
            if project_folder:
                mission_report_path = os.path.join(project_folder, 'mission_report.json')
                mission_report = {
                    'mission': 'Asset Retrieval',
                    'query': query,
                    'category': category,
                    'agent': 'SKIPPER',
                    'timestamp': datetime.now().isoformat(),
                    'assets_acquired': len(extracted_assets),
                    'assets': extracted_assets,
                    'log': self.mission_log[-10:]
                }
                
                with open(mission_report_path, 'w', encoding='utf-8') as f:
                    json.dump(mission_report, f, indent=2, ensure_ascii=False)
                
                self.log(f"Mission report saved: {mission_report_path}")
        
        self.log(f"=== MISSION COMPLETE ===")
        self.log(f"Assets acquired: {len(extracted_assets)}/{limit}")
        self.status = "MISSION COMPLETE"
        
        return extracted_assets
    
    def get_status(self):
        return {
            'agent': 'SKIPPER',
            'status': self.status,
            'operation': self.operation_name,
            'last_log': self.mission_log[-1] if self.mission_log else 'No activity',
            'total_missions': len([l for l in self.mission_log if 'MISSION START' in l])
        }