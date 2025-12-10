// src/core/session-manager.ts
import { Project } from './types';
import { VideoTimeline } from './timeline';

export class SessionManager {
    private sessionId: string;
    private currentProject: Project | null = null;
    private autoSaveInterval: number | null = null;
    private db: IDBDatabase | null = null;
    
    constructor() {
        // Generate unique session ID
        this.sessionId = 'vid_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        this.init();
    }
    
    private async init(): Promise<void> {
        console.log(`🎬 Session Manager Initialized: ${this.sessionId}`);
        
        // Update URL with session ID
        this.updateUrlWithSession();
        
        // Initialize IndexedDB
        await this.initIndexedDB();
        
        // Try to restore session from URL or last session
        await this.restoreSession();
        
        // Setup auto-save
        this.setupAutoSave();
        
        // Setup beforeunload listener
        window.addEventListener('beforeunload', () => this.saveCurrentSession());
        
        // Setup periodic cleanup
        setInterval(() => this.cleanupOldSessions(), 24 * 60 * 60 * 1000); // Daily
    }
    
    private updateUrlWithSession(): void {
        const url = new URL(window.location.href);
        url.searchParams.set('session', this.sessionId);
        window.history.replaceState({ sessionId: this.sessionId }, '', url);
        
        console.log(`🔗 Session URL: ${url.toString()}`);
    }
    
    private async initIndexedDB(): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('VideoEditorDB', 3);
            
            request.onerror = (event) => {
                console.error('IndexedDB error:', request.error);
                reject(request.error);
            };
            
            request.onsuccess = (event) => {
                this.db = (event.target as IDBOpenDBRequest).result;
                console.log('✅ IndexedDB initialized');
                resolve();
            };
            
            request.onupgradeneeded = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;
                const oldVersion = event.oldVersion;
                
                // Create or upgrade object stores
                if (!db.objectStoreNames.contains('sessions')) {
                    db.createObjectStore('sessions', { keyPath: 'sessionId' });
                }
                
                if (!db.objectStoreNames.contains('projects')) {
                    db.createObjectStore('projects', { keyPath: 'id' });
                }
                
                if (!db.objectStoreNames.contains('assets')) {
                    const store = db.createObjectStore('assets', { keyPath: 'id' });
                    store.createIndex('bySession', 'sessionId', { unique: false });
                }
                
                if (!db.objectStoreNames.contains('preferences')) {
                    db.createObjectStore('preferences', { keyPath: 'key' });
                }
                
                console.log(`🔄 IndexedDB upgraded from v${oldVersion} to v${db.version}`);
            };
        });
    }
    
    private async restoreSession(): Promise<void> {
        // Check URL for session parameter
        const urlParams = new URLSearchParams(window.location.search);
        const urlSessionId = urlParams.get('session');
        
        if (urlSessionId && urlSessionId !== this.sessionId) {
            // Try to load specific session from URL
            if (await this.loadSession(urlSessionId)) {
                this.sessionId = urlSessionId;
                this.updateUrlWithSession();
                return;
            }
        }
        
        // Try to load last session
        const lastSession = await this.getLastSession();
        if (lastSession) {
            await this.loadSession(lastSession.sessionId);
        } else {
            // Create new project
            this.createNewProject();
        }
    }
    
    private setupAutoSave(): void {
        // Auto-save every 30 seconds
        this.autoSaveInterval = window.setInterval(() => {
            this.saveCurrentSession();
        }, 30000);
        
        console.log('💾 Auto-save enabled (every 30 seconds)');
    }
    
    async createNewProject(name: string = 'Untitled Project'): Promise<Project> {
        const timeline = new VideoTimeline(`timeline_${Date.now()}`, name);
        
        this.currentProject = {
            id: this.sessionId,
            name: name,
            version: '1.0.0',
            timeline: timeline,
            assets: {
                videos: new Map(),
                audios: new Map(),
                images: new Map(),
                effects: new Map()
            },
            settings: {
                autoSave: true,
                autoSaveInterval: 30000,
                previewQuality: 'medium',
                renderQuality: 'high',
                defaultFrameRate: 30,
                defaultResolution: { width: 1920, height: 1080 }
            },
            metadata: {
                created: new Date(),
                modified: new Date(),
                author: 'Anonymous',
                description: '',
                tags: []
            }
        };
        
        // Save immediately
        await this.saveCurrentSession();
        
        // Dispatch event
        this.dispatchEvent('projectCreated', { project: this.currentProject });
        
        console.log(`📁 Created new project: ${name}`);
        return this.currentProject;
    }
    
    async saveCurrentSession(): Promise<void> {
        if (!this.currentProject || !this.db) return;
        
        try {
            // Update modification time
            this.currentProject.metadata.modified = new Date();
            
            // Prepare session data
            const sessionData = {
                sessionId: this.sessionId,
                project: this.serializeProject(this.currentProject),
                timestamp: Date.now(),
                lastModified: new Date().toISOString(),
                thumbnail: await this.generateThumbnail()
            };
            
            // Save to IndexedDB
            const transaction = this.db.transaction(['sessions', 'projects'], 'readwrite');
            
            // Save session
            const sessionStore = transaction.objectStore('sessions');
            sessionStore.put(sessionData);
            
            // Save project separately
            const projectStore = transaction.objectStore('projects');
            projectStore.put({
                id: this.currentProject.id,
                ...this.serializeProject(this.currentProject)
            });
            
            // Save assets
            await this.saveAssets();
            
            await transaction.complete;
            
            // Save to localStorage as backup
            localStorage.setItem(`video_editor_session_${this.sessionId}`, 
                JSON.stringify(sessionData));
            
            // Update URL with timestamp for cache busting
            this.updateUrlWithTimestamp();
            
            this.dispatchEvent('sessionSaved', { sessionId: this.sessionId });
            
            console.log(`💾 Session saved: ${this.sessionId}`);
            
        } catch (error) {
            console.error('Error saving session:', error);
            this.dispatchEvent('saveError', { error });
        }
    }
    
    private serializeProject(project: Project): any {
        // Convert complex objects to serializable format
        return {
            ...project,
            timeline: {
                ...project.timeline,
                // Remove non-serializable properties
                videoTracks: project.timeline.videoTracks.map(track => ({
                    ...track,
                    clips: track.clips.map(clip => this.serializeClip(clip))
                })),
                audioTracks: project.timeline.audioTracks.map(track => ({
                    ...track,
                    clips: track.clips.map(clip => this.serializeClip(clip))
                }))
            },
            assets: {
                // Store only metadata, not the actual files
                videos: Array.from(project.assets.videos.entries()).map(([id, file]) => ({
                    id,
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    lastModified: file.lastModified
                })),
                audios: Array.from(project.assets.audios.entries()).map(([id, file]) => ({
                    id,
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    lastModified: file.lastModified
                })),
                images: Array.from(project.assets.images.entries()).map(([id, file]) => ({
                    id,
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    lastModified: file.lastModified
                })),
                effects: Array.from(project.assets.effects.entries())
            }
        };
    }
    
    private serializeClip(clip: any): any {
        return {
            ...clip,
            // Remove non-serializable elements
            videoElement: undefined,
            canvasCache: undefined
        };
    }
    
    private async generateThumbnail(): Promise<string | null> {
        if (!this.currentProject?.timeline) return null;
        
        try {
            // Render first frame as thumbnail
            const canvas = await this.currentProject.timeline.renderFrame(0);
            return canvas.toDataURL('image/jpeg', 0.5);
        } catch (error) {
            console.warn('Failed to generate thumbnail:', error);
            return null;
        }
    }
    
    private updateUrlWithTimestamp(): void {
        const url = new URL(window.location.href);
        url.searchParams.set('t', Date.now().toString());
        window.history.replaceState({}, '', url);
    }
    
    private async saveAssets(): Promise<void> {
        if (!this.currentProject || !this.db) return;
        
        const transaction = this.db.transaction(['assets'], 'readwrite');
        const store = transaction.objectStore('assets');
        
        // Save video assets
        for (const [id, file] of this.currentProject.assets.videos) {
            const arrayBuffer = await file.arrayBuffer();
            store.put({
                id,
                sessionId: this.sessionId,
                type: 'video',
                name: file.name,
                data: arrayBuffer,
                mimeType: file.type,
                timestamp: Date.now()
            });
        }
        
        // Save audio assets
        for (const [id, file] of this.currentProject.assets.audios) {
            const arrayBuffer = await file.arrayBuffer();
            store.put({
                id,
                sessionId: this.sessionId,
                type: 'audio',
                name: file.name,
                data: arrayBuffer,
                mimeType: file.type,
                timestamp: Date.now()
            });
        }
        
        await transaction.complete;
    }
    
    async loadSession(sessionId: string): Promise<boolean> {
        try {
            // Try IndexedDB first
            const transaction = this.db!.transaction(['sessions', 'projects', 'assets'], 'readonly');
            const sessionStore = transaction.objectStore('sessions');
            const projectStore = transaction.objectStore('projects');
            
            const sessionRequest = sessionStore.get(sessionId);
            const projectRequest = projectStore.get(sessionId);
            
            const [sessionData, projectData] = await Promise.all([
                new Promise<any>((resolve, reject) => {
                    sessionRequest.onsuccess = () => resolve(sessionRequest.result);
                    sessionRequest.onerror = () => reject(sessionRequest.error);
                }),
                new Promise<any>((resolve, reject) => {
                    projectRequest.onsuccess = () => resolve(projectRequest.result);
                    projectRequest.onerror = () => reject(projectRequest.error);
                })
            ]);
            
            if (!sessionData || !projectData) {
                // Try localStorage as fallback
                const localStorageData = localStorage.getItem(`video_editor_session_${sessionId}`);
                if (localStorageData) {
                    return this.loadFromLocalStorage(sessionId, JSON.parse(localStorageData));
                }
                return false;
            }
            
            // Deserialize project
            this.currentProject = this.deserializeProject(projectData);
            this.sessionId = sessionId;
            
            // Load assets
            await this.loadAssets(sessionId);
            
            this.dispatchEvent('sessionLoaded', { 
                sessionId, 
                project: this.currentProject 
            });
            
            console.log(`📂 Session loaded: ${sessionId}`);
            return true;
            
        } catch (error) {
            console.error('Error loading session:', error);
            return false;
        }
    }
    
    private async loadAssets(sessionId: string): Promise<void> {
        if (!this.db || !this.currentProject) return;
        
        const transaction = this.db.transaction(['assets'], 'readonly');
        const store = transaction.objectStore('assets');
        const index = store.index('bySession');
        const request = index.getAll(sessionId);
        
        return new Promise((resolve, reject) => {
            request.onsuccess = async () => {
                const assets = request.result;
                
                for (const asset of assets) {
                    const blob = new Blob([asset.data], { type: asset.mimeType });
                    const file = new File([blob], asset.name, { 
                        type: asset.mimeType,
                        lastModified: asset.timestamp 
                    });
                    
                    switch (asset.type) {
                        case 'video':
                            this.currentProject!.assets.videos.set(asset.id, file);
                            break;
                        case 'audio':
                            this.currentProject!.assets.audios.set(asset.id, file);
                            break;
                    }
                }
                
                resolve();
            };
            
            request.onerror = () => reject(request.error);
        });
    }
    
    private loadFromLocalStorage(sessionId: string, data: any): boolean {
        try {
            this.currentProject = this.deserializeProject(data.project);
            this.sessionId = sessionId;
            console.log(`📂 Session loaded from localStorage: ${sessionId}`);
            return true;
        } catch (error) {
            console.error('Error loading from localStorage:', error);
            return false;
        }
    }
    
    private deserializeProject(data: any): Project {
        // Reconstruct complex objects
        // This would need custom logic based on your classes
        return data as Project;
    }
    
    async getLastSession(): Promise<{ sessionId: string, timestamp: number } | null> {
        if (!this.db) return null;
        
        return new Promise((resolve, reject) => {
            const transaction = this.db!.transaction(['sessions'], 'readonly');
            const store = transaction.objectStore('sessions');
            const request = store.openCursor(null, 'prev'); // Get last session
            
            request.onsuccess = (event) => {
                const cursor = (event.target as IDBRequest).result;
                if (cursor) {
                    resolve({
                        sessionId: cursor.value.sessionId,
                        timestamp: cursor.value.timestamp
                    });
                } else {
                    resolve(null);
                }
            };
            
            request.onerror = () => reject(request.error);
        });
    }
    
    async listSessions(): Promise<Array<{
        sessionId: string;
        name: string;
        timestamp: number;
        date: string;
        thumbnail?: string;
    }>> {
        if (!this.db) return [];
        
        return new Promise((resolve, reject) => {
            const transaction = this.db!.transaction(['sessions'], 'readonly');
            const store = transaction.objectStore('sessions');
            const request = store.getAll();
            
            request.onsuccess = (event) => {
                const sessions = (event.target as IDBRequest).result;
                const formatted = sessions.map((session: any) => ({
                    sessionId: session.sessionId,
                    name: session.project?.name || 'Unnamed Project',
                    timestamp: session.timestamp,
                    date: new Date(session.timestamp).toLocaleString(),
                    thumbnail: session.thumbnail
                })).sort((a, b) => b.timestamp - a.timestamp); // Newest first
                
                resolve(formatted);
            };
            
            request.onerror = () => reject(request.error);
        });
    }
    
    async deleteSession(sessionId: string): Promise<boolean> {
        if (!this.db) return false;
        
        try {
            const transaction = this.db.transaction(
                ['sessions', 'projects', 'assets'], 
                'readwrite'
            );
            
            // Delete from all stores
            transaction.objectStore('sessions').delete(sessionId);
            transaction.objectStore('projects').delete(sessionId);
            
            // Delete assets
            const assetStore = transaction.objectStore('assets');
            const index = assetStore.index('bySession');
            const request = index.getAllKeys(sessionId);
            
            request.onsuccess = () => {
                const keys = request.result;
                keys.forEach(key => assetStore.delete(key));
            };
            
            await transaction.complete;
            
            // Delete from localStorage
            localStorage.removeItem(`video_editor_session_${sessionId}`);
            
            this.dispatchEvent('sessionDeleted', { sessionId });
            
            console.log(`🗑️ Session deleted: ${sessionId}`);
            return true;
            
        } catch (error) {
            console.error('Error deleting session:', error);
            return false;
        }
    }
    
    private async cleanupOldSessions(): Promise<void> {
        const sessions = await this.listSessions();
        
        // Keep only last 20 sessions
        if (sessions.length > 20) {
            const toDelete = sessions.slice(20);
            
            for (const session of toDelete) {
                await this.deleteSession(session.sessionId);
            }
            
            console.log(`🧹 Cleaned up ${toDelete.length} old sessions`);
        }
    }
    
    getCurrentSessionId(): string {
        return this.sessionId;
    }
    
    getCurrentProject(): Project | null {
        return this.currentProject;
    }
    
    setCurrentProject(project: Project): void {
        this.currentProject = project;
        this.saveCurrentSession();
    }
    
    generateShareUrl(): string {
        const url = new URL(window.location.href);
        url.searchParams.set('session', this.sessionId);
        return url.toString();
    }
    
    exportProject(): { data: string, filename: string } {
        if (!this.currentProject) {
            throw new Error('No project to export');
        }
        
        const exportData = {
            ...this.serializeProject(this.currentProject),
            exportDate: new Date().toISOString(),
            exportFormat: 'videoeditor',
            version: '1.0'
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const filename = `${this.currentProject.name.replace(/\s+/g, '_')}_${Date.now()}.videoeditor`;
        
        return { data: dataStr, filename };
    }
    
    importProject(data: string): boolean {
        try {
            const importData = JSON.parse(data);
            this.currentProject = this.deserializeProject(importData);
            this.saveCurrentSession();
            
            this.dispatchEvent('projectImported', { project: this.currentProject });
            return true;
        } catch (error) {
            console.error('Error importing project:', error);
            return false;
        }
    }
    
    // Event system
    private events: Map<string, Function[]> = new Map();
    
    on(event: string, callback: Function): void {
        if (!this.events.has(event)) {
            this.events.set(event, []);
        }
        this.events.get(event)!.push(callback);
    }
    
    off(event: string, callback: Function): void {
        if (this.events.has(event)) {
            const callbacks = this.events.get(event)!;
            const index = callbacks.indexOf(callback);
            if (index !== -1) {
                callbacks.splice(index, 1);
            }
        }
    }
    
    private dispatchEvent(event: string, data?: any): void {
        if (this.events.has(event)) {
            this.events.get(event)!.forEach(callback => {
                callback(data);
            });
        }
    }
    
    // Cleanup
    destroy(): void {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
        
        window.removeEventListener('beforeunload', () => this.saveCurrentSession());
        
        // Save final state
        this.saveCurrentSession();
        
        console.log('👋 Session Manager destroyed');
    }
}

// Global instance
let globalSessionManager: SessionManager | null = null;

export function getSessionManager(): SessionManager {
    if (!globalSessionManager) {
        globalSessionManager = new SessionManager();
    }
    return globalSessionManager;
}

export function destroySessionManager(): void {
    if (globalSessionManager) {
        globalSessionManager.destroy();
        globalSessionManager = null;
    }
}