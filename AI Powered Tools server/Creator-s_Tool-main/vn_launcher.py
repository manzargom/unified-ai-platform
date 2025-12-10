# vn_launcher.py - SIMPLE WORKING VERSION
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import os
import json
from datetime import datetime

def main():
    root = tk.Tk()
    root.title("📖 Visual Novel Creator - GUI")
    root.geometry("700x600")
    root.configure(bg="#2c3e50")
    
    # Make sure projects folder exists
    os.makedirs("projects", exist_ok=True)
    
    # Title
    title = tk.Label(root, text="📖 VISUAL NOVEL CREATOR", 
                    font=("Arial", 20, "bold"),
                    bg="#2c3e50", fg="#ecf0f1")
    title.pack(pady=20)
    
    # Status
    status = tk.Label(root, text="Ready to create amazing stories!", 
                     font=("Arial", 10), bg="#2c3e50", fg="#bdc3c7")
    status.pack(pady=10)
    
    # Button Frame
    button_frame = tk.Frame(root, bg="#2c3e50")
    button_frame.pack(pady=20)
    
    def update_status(msg):
        status.config(text=msg)
        root.update()
    
    def create_project():
        name = simpledialog.askstring("New Project", "Enter project name:")
        if not name:
            return
        
        project_id = name.lower().replace(" ", "_")
        project_path = os.path.join("projects", project_id)
        
        if os.path.exists(project_path):
            messagebox.showerror("Error", f"Project '{name}' already exists!")
            return
        
        # Create project structure
        folders = ["characters", "scenes", "assets/backgrounds", "assets/characters", "assets/ui"]
        for folder in folders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        # Create project.json
        project_data = {
            "name": name,
            "created": datetime.now().isoformat(),
            "author": "Visual Novel Creator",
            "version": "1.0.0",
            "characters": [],
            "scenes": []
        }
        
        with open(os.path.join(project_path, "project.json"), "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=2)
        
        # Create basic Ren'Py script
        script_content = f"""# {name}
# Created with Visual Novel Creator
# Date: {datetime.now().strftime('%Y-%m-%d')}

define config.name = "{name}"
define config.version = "1.0"

label start:
    "Welcome to {name}!"
    "This is your story..."
    return
"""
        
        with open(os.path.join(project_path, "script.rpy"), "w", encoding="utf-8") as f:
            f.write(script_content)
        
        update_status(f"Project '{name}' created!")
        messagebox.showinfo("Success", f"Project '{name}' created at:\n{project_path}")
    
    def create_character():
        name = simpledialog.askstring("New Character", "Character name:")
        if not name:
            return
        
        role = simpledialog.askstring("Character Role", "Role (Hero, Villain, etc.):", initialvalue="Hero")
        description = simpledialog.askstring("Description", "Character description:", 
                                           initialvalue="A brave adventurer...")
        
        char_data = {
            "name": name,
            "role": role,
            "description": description,
            "created": datetime.now().isoformat()
        }
        
        update_status(f"Character '{name}' created")
        messagebox.showinfo("Character Created", 
                          f"Character: {name}\nRole: {role}\n\nDescription:\n{description}")
    
    def create_scene():
        title = simpledialog.askstring("New Scene", "Scene title:")
        if not title:
            return
        
        location = simpledialog.askstring("Location", "Scene location:", initialvalue="Forest")
        characters = simpledialog.askstring("Characters", "Characters (comma-separated):", 
                                          initialvalue="Hero, Villain")
        scene_text = simpledialog.askstring("Scene Text", "What happens:", 
                                          initialvalue="The characters meet...")
        
        scene_data = {
            "title": title,
            "location": location,
            "characters": [c.strip() for c in characters.split(",")],
            "text": scene_text,
            "created": datetime.now().isoformat()
        }
        
        update_status(f"Scene '{title}' created")
        messagebox.showinfo("Scene Created", 
                          f"Scene: {title}\nLocation: {location}\nCharacters: {characters}\n\nScene:\n{scene_text}")
    
    def list_projects():
        projects = []
        if os.path.exists("projects"):
            for item in os.listdir("projects"):
                if os.path.isdir(os.path.join("projects", item)):
                    projects.append(item)
        
        if projects:
            projects_text = "\n".join([f"• {p}" for p in projects])
            messagebox.showinfo("Your Projects", f"Found {len(projects)} projects:\n\n{projects_text}")
        else:
            messagebox.showinfo("No Projects", "No projects found. Create one first!")
    
    def show_help():
        help_text = """📖 VISUAL NOVEL CREATOR - GUI HELP

1. CREATE PROJECT
   • Start a new visual novel project
   • Creates organized folder structure
   • Generates Ren'Py script template

2. CREATE CHARACTER
   • Design characters for your story
   • Add names, roles, descriptions
   • Characters are saved to project

3. CREATE SCENE  
   • Write scenes with locations and characters
   • Add dialogue and descriptions
   • Build your story scene by scene

4. LIST PROJECTS
   • View all your created projects
   • Projects are saved in: projects/ folder

PROJECT STRUCTURE:
projects/
└── your_project/
    ├── project.json
    ├── script.rpy
    ├── characters/
    ├── scenes/
    └── assets/

Export to Ren'Py coming soon!"""
        messagebox.showinfo("Help Guide", help_text)
    
    # Buttons
    buttons = [
        ("🆕 CREATE PROJECT", create_project, "#3498db"),
        ("👤 CREATE CHARACTER", create_character, "#e74c3c"),
        ("🎭 CREATE SCENE", create_scene, "#2ecc71"),
        ("📁 LIST PROJECTS", list_projects, "#9b59b6"),
        ("📦 EXPORT (Coming Soon)", lambda: messagebox.showinfo("Coming Soon", "Export to Ren'Py coming in next update!"), "#f39c12"),
        ("❓ HELP", show_help, "#34495e"),
        ("🚪 EXIT", root.quit, "#7f8c8d")
    ]
    
    for text, command, color in buttons:
        btn = tk.Button(button_frame, text=text, command=command,
                       bg=color, fg="white", font=("Arial", 11, "bold"),
                       width=25, height=2, relief="raised", cursor="hand2")
        btn.pack(pady=5)
    
    # Log Area
    log_frame = tk.LabelFrame(root, text=" Activity Log ", font=("Arial", 10, "bold"),
                             bg="#2c3e50", fg="#3498db")
    log_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    log_text = scrolledtext.ScrolledText(log_frame, height=8, font=("Consolas", 9),
                                        bg="#34495e", fg="#ecf0f1")
    log_text.pack(fill="both", expand=True, padx=10, pady=10)
    log_text.insert("1.0", f"[{datetime.now().strftime('%H:%M:%S')}] GUI started\n")
    log_text.insert("2.0", "[+] Ready to create visual novels!\n")
    
    def log_message(msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_text.insert("end", f"[{timestamp}] {msg}\n")
        log_text.see("end")
    
    # Update buttons to also log
    original_create_project = create_project
    def logged_create_project():
        log_message("Creating new project...")
        original_create_project()
    
    original_create_character = create_character
    def logged_create_character():
        log_message("Creating character...")
        original_create_character()
    
    original_create_scene = create_scene
    def logged_create_scene():
        log_message("Creating scene...")
        original_create_scene()
    
    # Replace button commands
    for widget in button_frame.winfo_children():
        if isinstance(widget, tk.Button):
            text = widget.cget("text")
            if "CREATE PROJECT" in text:
                widget.config(command=logged_create_project)
            elif "CREATE CHARACTER" in text:
                widget.config(command=logged_create_character)
            elif "CREATE SCENE" in text:
                widget.config(command=logged_create_scene)
    
    print("✅ Visual Novel Creator GUI started!")
    print("📁 Projects folder: projects/")
    
    root.mainloop()

if __name__ == "__main__":
    main()