# creative_agent.py
"""
Creative Writing Agent with:
- Story development
- Character creation  
- World building
- Persistent memory
- Writing assistance
"""

import json
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import time

class CreativeAgent:
    """Enhanced agent for creative writing and storytelling"""
    
    def __init__(self, 
                 model: str = "deepseek-coder-6.7b-coder",
                 api_base: str = "http://localhost:1234/v1",
                 memory_dir: str = "data/memory"):
        self.model = model
        self.api_base = api_base
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # ADD THESE LINES:
        # Creative system prompt
        self.system_prompt = """You are Deepseek Creative - CREATIVE mode. Provide:
- Imaginative, engaging content
- Story and character development
- Worldbuilding details
- Creative problem-solving
- Collaborative brainstorming
Example style: "Let's create! Here's a concept: [idea]. We could develop it by: [suggestions]."""
        
        # Initialize memory
        
        # Creative writing system prompt
        self.creative_prompt = """YOU ARE A MASTER STORYTELLER AND CREATIVE WRITER

CREATIVE CAPABILITIES:
1. STORY DEVELOPMENT - Plot structures, narrative arcs, pacing, tension
2. CHARACTER CREATION - Deep character profiles, motivations, arcs, dialogue
3. WORLD BUILDING - Rich settings, lore, cultures, magic systems, technology
4. GENRE EXPERTISE - Fantasy, Sci-Fi, Mystery, Romance, Horror, Historical, etc.
5. WRITING STYLES - Descriptive prose, dialogue, exposition, show-don't-tell
6. EDITING & REVISION - Improving drafts, fixing pacing, enhancing prose

CREATIVE PRINCIPLES:
- Create ORIGINAL, compelling content
- Build EMOTIONAL connections with characters
- Maintain CONSISTENCY in world-building
- Use VIVID, sensory language
- Balance ACTION, DIALOGUE, and DESCRIPTION
- Respect established lore and character traits

FORMATTING:
- Use markdown for organization
- Separate sections clearly
- Include examples when helpful
- Suggest improvements and alternatives

YOU ARE: Imaginative, detailed, consistent, and passionate about storytelling.
"""
        
        # Initialize creative state
        self.current_project = None
        self.characters = {}
        self.worlds = {}
        self.stories = {}
        self.inspirations = []
        
        # Load existing creative works
        self.load_creative_memory()
        
        # Conversation with creative context
        self.conversation = [{"role": "system", "content": self.system_prompt}]
        
        # Add loaded creative context to conversation
        self._add_creative_context()
    
    def _add_creative_context(self):
        """Add loaded creative works to context"""
        context_parts = []
        
        if self.current_project:
            context_parts.append(f"CURRENT PROJECT: {self.current_project['title']}")
            context_parts.append(f"Genre: {self.current_project.get('genre', 'Not specified')}")
            context_parts.append(f"Status: {self.current_project.get('status', 'In progress')}")
        
        if self.characters:
            context_parts.append(f"\nCHARACTERS IN MEMORY: {len(self.characters)}")
            for name, char in list(self.characters.items())[:3]:  # Show first 3
                context_parts.append(f"- {name}: {char.get('role', 'Character')}")
        
        if self.stories:
            context_parts.append(f"\nSTORIES IN MEMORY: {len(self.stories)}")
            for title, story in list(self.stories.items())[:2]:
                context_parts.append(f"- {title}: {story.get('genre', 'Story')}")
        
        if context_parts:
            context_message = "\n".join(context_parts)
            self.conversation.append({
                "role": "system",
                "content": f"CURRENT CREATIVE CONTEXT:\n{context_message}\n\nUse this context in your responses."
            })
    
    def send_message(self, user_message: str, creative_mode: str = "general") -> str:
        """Send message with creative enhancements"""
        
        # Add creative mode context
        mode_context = {
            "story": "Focus on story development, plot, and narrative structure.",
            "character": "Focus on character creation, development, and relationships.",
            "world": "Focus on world-building, settings, and lore.",
            "writing": "Focus on writing style, prose, and editing.",
            "general": "Creative writing assistance across all areas."
        }.get(creative_mode, "Creative writing assistance.")
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": message}
        ]
        
        self.conversation.append({"role": "user", "content": enhanced_message})
        
        payload = {
            "model": self.model,
            "messages": self.conversation,
            "temperature": 0.85,  # Higher for creativity
            "max_tokens": 3000,   # Longer for detailed creative work
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                json=payload,
                timeout=180  # Longer timeout for creative work
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_reply = result["choices"][0]["message"]["content"]
                self.conversation.append({"role": "assistant", "content": assistant_reply})
                
                # Auto-save creative elements from response
                self._extract_and_save_creative_elements(user_message, assistant_reply)
                
                return assistant_reply
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _extract_and_save_creative_elements(self, user_input: str, response: str):
        """Extract potential creative elements from response for saving"""
        # This is a simple extraction - could be enhanced with more sophisticated parsing
        
        # Check for character mentions
        if "character named" in response.lower() or "protagonist" in response.lower():
            # Simple extraction for demo - in production you'd want more sophisticated parsing
            pass
        
        # Auto-save if user is clearly creating something
        save_triggers = [
            "create a character named",
            "new character:",
            "story about",
            "world called",
            "setting:",
            "plot:"
        ]
        
        for trigger in save_triggers:
            if trigger in user_input.lower():
                self.save_creative_memory()
                break
    
    # ===== CREATIVE FUNCTIONS =====
    
    def create_character(self, name: str, attributes: Dict[str, Any]) -> str:
        """Create and save a character"""
        character_id = f"char_{len(self.characters) + 1:04d}"
        
        character = {
            "id": character_id,
            "name": name,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            **attributes
        }
        
        self.characters[name] = character
        self.save_creative_memory()
        
        # Generate character profile using AI
        prompt = f"""Create a detailed character profile for {name}.

Character attributes: {json.dumps(attributes, indent=2)}

Include:
1. Physical description
2. Personality traits
3. Background story
4. Motivations and goals
5. Strengths and weaknesses
6. Character arc potential
7. Relationships with others
8. Key quotes or dialogue style

Make this character feel real and compelling."""
        
        return self.send_message(prompt, creative_mode="character")
    
    def develop_story(self, title: str, genre: str, premise: str) -> str:
        """Develop a story outline"""
        story_id = f"story_{len(self.stories) + 1:04d}"
        
        story = {
            "id": story_id,
            "title": title,
            "genre": genre,
            "premise": premise,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "outline": {},
            "chapters": [],
            "characters": [],
            "settings": []
        }
        
        self.stories[title] = story
        self.current_project = story
        self.save_creative_memory()
        
        # Generate story development using AI
        prompt = f"""Develop a story titled "{title}" in the {genre} genre.

Premise: {premise}

Create a comprehensive story development including:
1. Logline (one-sentence summary)
2. Three-act structure
3. Major plot points
4. Character roster needed
5. Key settings/locations
6. Central conflict
7. Themes to explore
8. Opening scene ideas
9. Potential ending options
10. Writing style suggestions for this genre

Make this an engaging, well-structured story framework."""
        
        return self.send_message(prompt, creative_mode="story")
    
    def build_world(self, name: str, genre: str, description: str) -> str:
        """Build a fictional world"""
        world_id = f"world_{len(self.worlds) + 1:04d}"
        
        world = {
            "id": world_id,
            "name": name,
            "genre": genre,
            "description": description,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "locations": {},
            "cultures": {},
            "magic_systems": {},
            "technology": {},
            "history": {},
            "races_species": {}
        }
        
        self.worlds[name] = world
        self.save_creative_memory()
        
        # Generate world-building using AI
        prompt = f"""Build a fictional world called "{name}" in the {genre} genre.

Initial description: {description}

Develop a comprehensive world including:
1. Physical geography and maps
2. Major cultures and societies
3. Political systems and conflicts
4. Magic systems OR technology (depending on genre)
5. History and major events
6. Economics and trade
7. Religion and beliefs
8. Daily life for inhabitants
9. Unique creatures/races
10. Key locations with descriptions

Make this world feel rich, consistent, and immersive."""
        
        return self.send_message(prompt, creative_mode="world")
    
    def writing_assistance(self, text: str, feedback_type: str = "general") -> str:
        """Get writing assistance and feedback"""
        
        feedback_types = {
            "prose": "Focus on prose quality, word choice, and sentence structure.",
            "dialogue": "Focus on dialogue authenticity, character voice, and pacing.",
            "description": "Focus on sensory details, showing vs telling, and immersion.",
            "pacing": "Focus on story pacing, scene transitions, and tension.",
            "structure": "Focus on plot structure, scene order, and narrative flow.",
            "general": "General writing feedback and improvements."
        }
        
        focus = feedback_types.get(feedback_type, "General writing feedback.")
        
        prompt = f"""Provide writing feedback and assistance.

Text to review:
{text}

Feedback focus: {feedback_type}
{focus}

Please provide:
1. Overall assessment
2. Strengths of the writing
3. Areas for improvement
4. Specific suggestions for revision
5. Examples of improved versions
6. Tips for this type of writing

Be constructive, specific, and helpful."""
        
        return self.send_message(prompt, creative_mode="writing")
    
    def generate_scene(self, context: str, scene_type: str) -> str:
        """Generate a scene based on context"""
        
        scene_types = {
            "opening": "An opening scene that hooks the reader",
            "climax": "A climactic scene with high tension",
            "quiet": "A quiet character moment",
            "action": "An action-packed sequence",
            "dialogue": "A dialogue-heavy scene",
            "descriptive": "A richly descriptive scene"
        }
        
        scene_desc = scene_types.get(scene_type, "A well-written scene")
        
        prompt = f"""Generate a {scene_type} scene.

Context: {context}

This should be a {scene_desc}.

Write the scene including:
1. Setting description
2. Character actions and dialogue
3. Sensory details
4. Emotional tone
5. Pacing appropriate for this scene type
6. Show-don't-tell techniques
7. A satisfying scene arc

Write the full scene with proper formatting."""
        
        return self.send_message(prompt, creative_mode="writing")
    
    # ===== MEMORY MANAGEMENT =====
    
    def save_creative_memory(self):
        """Save all creative works to disk"""
        creative_data = {
            "characters": self.characters,
            "worlds": self.worlds,
            "stories": self.stories,
            "current_project": self.current_project,
            "inspirations": self.inspirations,
            "last_saved": datetime.now().isoformat()
        }
        
        # Save as JSON
        json_file = self.memory_dir / "creative_works.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(creative_data, f, indent=2, ensure_ascii=False)
        
        # Also save as pickle for Python objects
        pickle_file = self.memory_dir / "creative_works.pkl"
        with open(pickle_file, 'wb') as f:
            pickle.dump(creative_data, f)
        
        print(f"✓ Creative memory saved: {len(self.characters)} characters, "
              f"{len(self.worlds)} worlds, {len(self.stories)} stories")
    
    def load_creative_memory(self):
        """Load creative works from disk"""
        json_file = self.memory_dir / "creative_works.json"
        
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    creative_data = json.load(f)
                
                self.characters = creative_data.get("characters", {})
                self.worlds = creative_data.get("worlds", {})
                self.stories = creative_data.get("stories", {})
                self.current_project = creative_data.get("current_project")
                self.inspirations = creative_data.get("inspirations", [])
                
                print(f"✓ Creative memory loaded: {len(self.characters)} characters, "
                      f"{len(self.worlds)} worlds, {len(self.stories)} stories")
                      
            except Exception as e:
                print(f"Note: Could not load creative memory: {e}")
        else:
            print("Note: No existing creative memory found. Starting fresh.")
    
    def list_creative_works(self) -> str:
        """List all creative works in memory"""
        if not any([self.characters, self.worlds, self.stories]):
            return "No creative works in memory yet. Create something!"
        
        output = ["=== CREATIVE WORKS IN MEMORY ==="]
        
        if self.characters:
            output.append(f"\nCHARACTERS ({len(self.characters)}):")
            for name, char in self.characters.items():
                role = char.get('role', 'Character')
                created = char.get('created', 'Unknown')[:10]
                output.append(f"  • {name} - {role} (Created: {created})")
        
        if self.worlds:
            output.append(f"\nWORLDS ({len(self.worlds)}):")
            for name, world in self.worlds.items():
                genre = world.get('genre', 'Unknown')
                created = world.get('created', 'Unknown')[:10]
                output.append(f"  • {name} - {genre} world (Created: {created})")
        
        if self.stories:
            output.append(f"\nSTORIES ({len(self.stories)}):")
            for title, story in self.stories.items():
                genre = story.get('genre', 'Unknown')
                created = story.get('created', 'Unknown')[:10]
                output.append(f"  • {title} - {genre} (Created: {created})")
        
        if self.current_project:
            output.append(f"\nCURRENT PROJECT:")
            output.append(f"  • {self.current_project.get('title', 'Untitled')}")
            output.append(f"    Genre: {self.current_project.get('genre', 'Not specified')}")
            output.append(f"    Status: {self.current_project.get('status', 'In progress')}")
        
        return "\n".join(output)
    
    def clear_history(self):
        """Clear conversation but keep creative prompt and memory"""
         self.conversation = [{"role": "system", "content": self.system_prompt}]
        self._add_creative_context()
    
    def interactive_creative_session(self):
        """Interactive creative writing session"""
        print("="*70)
        print("CREATIVE WRITING AGENT - Master Storyteller")
        print("="*70)
        print(f"Memory: {len(self.characters)} chars, {len(self.worlds)} worlds, {len(self.stories)} stories")
        print("-"*70)
        print("CREATIVE MODES: story, character, world, writing, general")
        print("SPECIAL COMMANDS:")
        print("  'new character <name> <attributes>' - Create character")
        print("  'new story <title> <genre> <premise>' - Start story")
        print("  'new world <name> <genre> <desc>' - Build world")
        print("  'feedback <type> <text>' - Writing feedback")
        print("  'scene <type> <context>' - Generate scene")
        print("  'list' - List all creative works")
        print("  'save' - Save creative memory")
        print("  'clear' - Clear conversation")
        print("  'exit' - Exit")
        print("="*70)
        
        while True:
            try:
                user_input = input("\n🎨 Creative Mode: ").strip()
                
                if user_input.lower() == 'exit':
                    print("Saving creative works...")
                    self.save_creative_memory()
                    print("Creative session ended.")
                    break
                
                elif user_input.lower() == 'clear':
                    self.clear_history()
                    print("✓ Conversation cleared, creative memory preserved")
                    continue
                
                elif user_input.lower() == 'list':
                    print(self.list_creative_works())
                    continue
                
                elif user_input.lower() == 'save':
                    self.save_creative_memory()
                    continue
                
                # Parse special creative commands
                response = self._parse_creative_command(user_input)
                if response:
                    print(f"\n{response}")
                    continue
                
                # Default: creative chat
                if not user_input:
                    continue
                
                # Determine creative mode from input
                creative_mode = self._detect_creative_mode(user_input)
                
                print("Creating...", end="", flush=True)
                start = time.time()
                response = self.send_message(user_input, creative_mode)
                elapsed = time.time() - start
                print(f"\r✍️  Creative Assistant ({elapsed:.1f}s): {response}")
                
            except KeyboardInterrupt:
                print("\n\nSaving creative works before exit...")
                self.save_creative_memory()
                print("Creative session saved.")
                break
            except Exception as e:
                print(f"\nError: {e}")
    
    def _detect_creative_mode(self, text: str) -> str:
        """Detect which creative mode to use based on input"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['character', 'protagonist', 'hero', 'villain']):
            return "character"
        elif any(word in text_lower for word in ['story', 'plot', 'narrative', 'scene']):
            return "story"
        elif any(word in text_lower for word in ['world', 'setting', 'universe', 'lore']):
            return "world"
        elif any(word in text_lower for word in ['write', 'prose', 'dialogue', 'description']):
            return "writing"
        else:
            return "general"
    
    def _parse_creative_command(self, command: str) -> Optional[str]:
        """Parse special creative commands"""
        command_lower = command.lower()
        
        if command_lower.startswith('new character '):
            parts = command[14:].split(' ', 1)
            if len(parts) == 2:
                name, attr_str = parts
                try:
                    # Try to parse attributes as JSON
                    import json
                    attributes = json.loads(attr_str)
                    return self.create_character(name, attributes)
                except:
                    # If not JSON, use as description
                    attributes = {"description": attr_str}
                    return self.create_character(name, attributes)
        
        elif command_lower.startswith('new story '):
            parts = command[10:].split(' ', 2)
            if len(parts) == 3:
                title, genre, premise = parts
                return self.develop_story(title, genre, premise)
        
        elif command_lower.startswith('new world '):
            parts = command[10:].split(' ', 2)
            if len(parts) == 3:
                name, genre, description = parts
                return self.build_world(name, genre, description)
        
        elif command_lower.startswith('feedback '):
            parts = command[9:].split(' ', 1)
            if len(parts) == 2:
                feedback_type, text = parts
                return self.writing_assistance(text, feedback_type)
        
        elif command_lower.startswith('scene '):
            parts = command[6:].split(' ', 1)
            if len(parts) == 2:
                scene_type, context = parts
                return self.generate_scene(context, scene_type)
        
        return None

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data/memory", exist_ok=True)
    
    agent = CreativeAgent()
    agent.interactive_creative_session()