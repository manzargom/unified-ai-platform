# agents/kowalski.py - Creative Analysis Agent
import json
import os
from datetime import datetime

class Kowalski:
    def __init__(self, skipper_agent=None):
        self.skipper = skipper_agent
        self.analysis_log = []
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] ANALYSIS: {message}"
        self.analysis_log.append(log_entry)
        print(f"🔬 KOWALSKI: {message}")
        return log_entry
    
    def analyze_story_request(self, prompt):
        self.log(f"Analyzing story request: {prompt[:50]}...")
        
        analysis = {
            'prompt': prompt,
            'genre': self.analyze_genre(prompt),
            'tone': self.analyze_tone(prompt),
            'required_assets': [],
            'character_count': self.count_characters(prompt),
            'location_count': self.count_locations(prompt),
            'complexity_score': self.calculate_complexity(prompt)
        }
        
        if 'forest' in prompt.lower() or 'woods' in prompt.lower():
            analysis['required_assets'].append({'type': 'background', 'query': 'fantasy forest', 'priority': 'HIGH'})
        
        if 'castle' in prompt.lower() or 'palace' in prompt.lower():
            analysis['required_assets'].append({'type': 'background', 'query': 'fantasy castle', 'priority': 'HIGH'})
        
        if 'character' in prompt.lower() or 'hero' in prompt.lower():
            analysis['required_assets'].append({'type': 'character', 'query': 'fantasy hero', 'priority': 'HIGH'})
        
        if 'village' in prompt.lower() or 'town' in prompt.lower():
            analysis['required_assets'].append({'type': 'background', 'query': 'fantasy village', 'priority': 'MEDIUM'})
        
        self.log(f"Analysis complete. Required assets: {len(analysis['required_assets'])}")
        
        return analysis
    
    def analyze_genre(self, prompt):
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['fantasy', 'magic', 'dragon', 'elf', 'wizard']):
            return 'FANTASY'
        elif any(word in prompt_lower for word in ['sci-fi', 'space', 'future', 'robot', 'cyber']):
            return 'SCIENCE_FICTION'
        elif any(word in prompt_lower for word in ['romance', 'love', 'heart', 'date']):
            return 'ROMANCE'
        elif any(word in prompt_lower for word in ['mystery', 'detective', 'crime', 'secret']):
            return 'MYSTERY'
        elif any(word in prompt_lower for word in ['horror', 'scary', 'ghost', 'monster']):
            return 'HORROR'
        else:
            return 'GENERAL'
    
    def analyze_tone(self, prompt):
        prompt_lower = prompt.lower()
        
        positive_words = ['happy', 'joy', 'love', 'peace', 'fun']
        negative_words = ['dark', 'sad', 'angry', 'fear', 'death']
        mysterious_words = ['secret', 'mystery', 'unknown', 'hidden']
        
        positive_count = sum(1 for word in positive_words if word in prompt_lower)
        negative_count = sum(1 for word in negative_words if word in prompt_lower)
        mysterious_count = sum(1 for word in mysterious_words if word in prompt_lower)
        
        if mysterious_count > 2:
            return 'MYSTERIOUS'
        elif negative_count > positive_count:
            return 'DARK'
        elif positive_count > negative_count:
            return 'LIGHTHEARTED'
        else:
            return 'NEUTRAL'
    
    def count_characters(self, prompt):
        character_words = ['he', 'she', 'they', 'character', 'hero', 'villain', 'person']
        words = prompt.lower().split()
        return sum(1 for word in words if word in character_words)
    
    def count_locations(self, prompt):
        location_words = ['forest', 'castle', 'room', 'city', 'village', 'street', 'house']
        words = prompt.lower().split()
        return sum(1 for word in words if word in location_words)
    
    def calculate_complexity(self, prompt):
        words = len(prompt.split())
        sentences = prompt.count('.') + prompt.count('!') + prompt.count('?')
        
        complexity = min(10, (words / 20) + (sentences * 2))
        return round(complexity, 1)
    
    def create_asset_retrieval_plan(self, analysis, project_folder):
        self.log("Creating asset retrieval plan...")
        
        plan = {
            'project_folder': project_folder,
            'analysis': analysis,
            'asset_requests': [],
            'estimated_time': '5-10 minutes',
            'agent_coordination': 'SKIPPER dispatched'
        }
        
        for asset_req in analysis['required_assets']:
            request = {
                'query': asset_req['query'],
                'category': asset_req['type'] + 's',
                'priority': asset_req['priority'],
                'quantity': 2 if asset_req['priority'] == 'HIGH' else 1
            }
            plan['asset_requests'].append(request)
        
        self.log(f"Plan created: {len(plan['asset_requests'])} asset requests")
        
        return plan
    
    def coordinate_with_skipper(self, plan):
        if not self.skipper:
            self.log("ERROR: Skipper agent not available")
            return []
        
        retrieved_assets = []
        
        for request in plan['asset_requests']:
            self.log(f"Dispatching Skipper for: {request['query']}")
            
            assets = self.skipper.full_mission(
                query=request['query'],
                category=request['category'],
                project_folder=plan['project_folder'],
                limit=request['quantity']
            )
            
            retrieved_assets.extend(assets)
        
        return retrieved_assets