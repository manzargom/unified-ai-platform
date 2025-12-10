// session-manager.js - Simple Session Management
class SessionManager {
    constructor() {
        this.sessionId = 'vid_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        this.project = null;
        this.init();
    }
    
    init() {
        console.log('🎬 Session Manager initialized:', this.sessionId);
        
        // Update URL
        const url = new URL(window.location);
        url.searchParams.set('session', this.sessionId);
        window.history.replaceState({}, '', url);
        
        // Try to load existing session
        this.loadSession();
        
        // Setup auto-save
        setInterval(() => this.save(), 30000);
        
        // Save on page unload
        window.addEventListener('beforeunload', () => this.save());
    }
    
    loadSession() {
        const urlParams = new URLSearchParams(window.location.search);
        const sessionParam = urlParams.get('session');
        
        if (sessionParam && sessionParam !== this.sessionId) {
            // Try to load specific session
            const saved = localStorage.getItem(`video_editor_${sessionParam}`);
            if (saved) {
                this.sessionId = sessionParam;
                this.project = JSON.parse(saved);
                console.log('📂 Loaded existing session');
                this.updateUI();
                return;
            }
        }
        
        // Create new project
        this.createNewProject();
    }
    
    createNewProject(name = 'Untitled Project') {
        this.project = {
            id: this.sessionId,
            name: name,
            created: new Date().toISOString(),
            modified: new Date().toISOString(),
            tracks: {
                video: [{ id: 'v1', clips: [], muted: false, locked: false }],
                audio: [{ id: 'a1', clips: [], muted: false, locked: false }]
            },
            currentTime: 0,
            duration: 0,
            settings: {
                resolution: '1920x1080',
                fps: 30
            }
        };
        
        this.save();
        this.updateUI();
        console.log('📁 Created new project:', name);
    }
    
    save() {
        if (!this.project) return;
        
        this.project.modified = new Date().toISOString();
        localStorage.setItem(`video_editor_${this.sessionId}`, JSON.stringify(this.project));
        console.log('💾 Auto-saved project');
    }
    
    updateUI() {
        // Update session ID display
        const sessionEl = document.getElementById('sessionId');
        if (sessionEl) {
            sessionEl.textContent = this.sessionId;
        }
        
        // Update project info
        if (this.project) {
            const detailsEl = document.getElementById('projectDetails');
            if (detailsEl) {
                detailsEl.innerHTML = `
                    <p><strong>${this.project.name}</strong></p>
                    <p>Created: ${new Date(this.project.created).toLocaleString()}</p>
                    <p>Video Tracks: ${this.project.tracks.video.length}</p>
                    <p>Audio Tracks: ${this.project.tracks.audio.length}</p>
                `;
            }
        }
    }
    
    getShareUrl() {
        const url = new URL(window.location.href);
        url.searchParams.set('session', this.sessionId);
        return url.toString();
    }
    
    copySessionId() {
        navigator.clipboard.writeText(this.sessionId).then(() => {
            this.showNotification('Session ID copied to clipboard!');
        });
    }
    
    showNotification(message, type = 'info') {
        // Create a simple notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #1e1e2e;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            border-left: 4px solid ${type === 'success' ? '#2ecc71' : '#ff5e00'};
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.remove(), 3000);
    }
}

// Create global instance
window.sessionManager = new SessionManager();