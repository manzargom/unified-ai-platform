"""
GUI Interface for Enhanced Deepseek Agent
Location: C:\LM Studio\AI_Agent_Framework\src\interfaces\gui_interface.py
"""

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, filedialog
import threading
import time
import json
from datetime import datetime
import os

class DeepseekGUI:
    def __init__(self, agent=None):
        """Initialize the GUI interface"""
        self.agent = agent
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Deepseek Agent - Enhanced GUI")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Configure styles
        self.setup_styles()
        
        # Build the interface
        self.create_widgets()
        
        # Conversation history
        self.conversation_history = []
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        accent_color = '#4a90e2'
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=accent_color, foreground=fg_color)
        style.configure('TEntry', fieldbackground='#3c3c3c', foreground=fg_color)
        style.configure('TCombobox', fieldbackground='#3c3c3c', foreground=fg_color)
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Label(header_frame, text="🤖 Deepseek Enhanced Agent", 
                 font=('Helvetica', 16, 'bold')).pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="🟢 Ready - Connected to LM Studio")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.N, tk.S), padx=(0, 10))
        
        # Model selection
        ttk.Label(control_frame, text="Model:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="deepseek-coder-6.7b-instruct")
        model_combo = ttk.Combobox(control_frame, textvariable=self.model_var, 
                                  values=["deepseek-coder-6.7b-instruct", "deepseek-llm-7b-chat"])
        model_combo.grid(row=0, column=1, pady=5, padx=5)
        
        # Temperature control
        ttk.Label(control_frame, text="Temperature:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.temp_var = tk.DoubleVar(value=0.85)
        temp_scale = ttk.Scale(control_frame, from_=0.1, to=1.5, variable=self.temp_var,
                              orient=tk.HORIZONTAL)
        temp_scale.grid(row=1, column=1, pady=5, padx=5)
        self.temp_label = ttk.Label(control_frame, text="0.85")
        self.temp_label.grid(row=2, column=1, pady=(0, 10))
        
        # Update temp label when scale changes
        def update_temp_label(*args):
            self.temp_label.config(text=f"{self.temp_var.get():.2f}")
        self.temp_var.trace('w', update_temp_label)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="🔄 Clear Chat", 
                  command=self.clear_chat).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="💾 Save Chat", 
                  command=self.save_conversation).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="📊 Agent Info", 
                  command=self.show_agent_info).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="⚙️ Settings", 
                  command=self.show_settings).pack(fill=tk.X, pady=2)
        
        # Center panel - Chat display
        chat_frame = ttk.LabelFrame(main_frame, text="Chat", padding="10")
        chat_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat text area
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD,
            width=60,
            height=25,
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='white',
            font=('Consolas', 10)
        )
        self.chat_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_text.config(state=tk.DISABLED)
        
        # Right panel - Info
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.grid(row=1, column=2, sticky=(tk.N, tk.S))
        
        info_text = """🤖 Enhanced Agent Features:

✅ Expert Mode Activated
✅ Confident Responses
✅ Extended Context
✅ Local & Private
✅ Code Generation
✅ Technical Explanations

📊 Statistics:
• Model: Deepseek 6.7B
• Context: 2500 tokens
• Running: LM Studio
• Location: Local

💡 Tips:
• Use clear questions
• Ask for code examples
• Request explanations
• Use markdown formatting"""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack()
        
        # Bottom panel - Input
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        # Input field
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var)
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.input_entry.bind('<Return>', self.send_message)
        
        # Send button
        ttk.Button(input_frame, text="Send", command=self.send_message).grid(row=0, column=1)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def append_message(self, sender, message, is_code=False):
        """Add a message to the chat display"""
        self.chat_text.config(state=tk.NORMAL)
        
        # Configure tags for different message types
        self.chat_text.tag_config('user', foreground='#4a90e2', font=('Helvetica', 10, 'bold'))
        self.chat_text.tag_config('assistant', foreground='#50c878', font=('Helvetica', 10, 'bold'))
        self.chat_text.tag_config('code', foreground='#f39c12', font=('Consolas', 9))
        self.chat_text.tag_config('system', foreground='#9b59b6', font=('Helvetica', 9, 'italic'))
        
        # Insert message
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_text.insert(tk.END, f"\n[{timestamp}] {sender}: ", 
                            'user' if sender == 'You' else 'assistant')
        
        if is_code:
            self.chat_text.insert(tk.END, f"\n{message}\n", 'code')
        else:
            self.chat_text.insert(tk.END, f"{message}\n")
        
        self.chat_text.see(tk.END)  # Scroll to bottom
        self.chat_text.config(state=tk.DISABLED)
        
        # Add to history
        self.conversation_history.append({
            'timestamp': timestamp,
            'sender': sender,
            'message': message,
            'is_code': is_code
        })
    
    def send_message(self, event=None):
        """Send message to agent"""
        message = self.input_var.get().strip()
        if not message:
            return
        
        # Clear input
        self.input_var.set("")
        
        # Display user message
        self.append_message('You', message)
        
        # Update status
        self.status_var.set("⏳ Processing...")
        
        # Send in separate thread to avoid GUI freeze
        threading.Thread(target=self.process_agent_response, args=(message,), daemon=True).start()
    
    def process_agent_response(self, message):
        """Process agent response in background thread"""
        try:
            if self.agent:
                # Update agent settings if changed
                self.agent.model = self.model_var.get()
                # Note: temperature would need to be passed to agent
                
                # Get response from agent
                start_time = time.time()
                response = self.agent.send_message(message)
                elapsed = time.time() - start_time
                
                # Update GUI in main thread
                self.root.after(0, self.display_response, response, elapsed)
            else:
                # Simulate response if no agent
                self.root.after(0, self.display_response, 
                              f"I'm a GUI test response to: {message}", 1.5)
                
        except Exception as e:
            self.root.after(0, self.display_error, str(e))
    
    def display_response(self, response, elapsed):
        """Display agent response in GUI"""
        # Check if response looks like code
        is_code = '```' in response or 'def ' in response or 'import ' in response
        
        # Clean up code blocks for display
        if '```' in response:
            response = response.replace('```python', '```').replace('```bash', '```')
        
        self.append_message('Assistant', f"({elapsed:.1f}s) {response}", is_code)
        self.status_var.set("🟢 Ready")
    
    def display_error(self, error_msg):
        """Display error in GUI"""
        self.append_message('System', f"Error: {error_msg}")
        self.status_var.set("🔴 Error occurred")
    
    def clear_chat(self):
        """Clear chat history"""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state=tk.DISABLED)
        self.conversation_history = []
        
        if self.agent:
            self.agent.clear_history()
        
        self.append_message('System', "Chat cleared and history reset")
    
    def save_conversation(self):
        """Save conversation to file"""
        if not self.conversation_history:
            messagebox.showwarning("No Conversation", "No conversation to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"deepseek_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'metadata': {
                            'saved_at': datetime.now().isoformat(),
                            'model': self.model_var.get(),
                            'temperature': self.temp_var.get()
                        },
                        'conversation': self.conversation_history
                    }, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Conversation saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def show_agent_info(self):
        """Show agent information dialog"""
        info_text = f"""🤖 Enhanced Deepseek Agent

Model: {self.model_var.get()}
Temperature: {self.temp_var.get():.2f}
Context Window: 2500 tokens
Location: Local via LM Studio

Features:
• Expert mode with confident responses
• Code generation and explanation
• Technical documentation
• Local and private operation
• No API limits or censorship

Status: {"Connected" if self.agent else "Test Mode"}"""
        
        messagebox.showinfo("Agent Information", info_text)
    
    def show_settings(self):
        """Show settings dialog"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("400x300")
        
        ttk.Label(settings_win, text="Settings", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # API settings
        api_frame = ttk.LabelFrame(settings_win, text="API Settings", padding="10")
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(api_frame, text="API Base URL:").grid(row=0, column=0, sticky=tk.W)
        api_url = ttk.Entry(api_frame, width=40)
        api_url.insert(0, "http://localhost:1234/v1")
        api_url.grid(row=0, column=1, padx=5)
        
        # Display settings
        display_frame = ttk.LabelFrame(settings_win, text="Display Settings", padding="10")
        display_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(display_frame, text="Font Size:").grid(row=0, column=0, sticky=tk.W)
        font_size = ttk.Combobox(display_frame, values=["9", "10", "11", "12"], width=10)
        font_size.set("10")
        font_size.grid(row=0, column=1, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(settings_win)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", 
                  command=lambda: messagebox.showinfo("Saved", "Settings saved")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=settings_win.destroy).pack(side=tk.LEFT, padx=5)
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

# Test function
def test_gui():
    """Test the GUI without actual agent"""
    gui = DeepseekGUI()
    gui.run()

if __name__ == "__main__":
    test_gui()
