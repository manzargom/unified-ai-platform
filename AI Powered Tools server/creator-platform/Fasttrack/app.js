// app.js - Main Application Logic
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎬 Video Editor Starting...');
    
    // Initialize components
    initVideoPlayer();
    initTimeline();
    initEventListeners();
    
    // Check server connection
    checkServerHealth();
    
    console.log('✅ Editor ready!');
});

// Initialize video player
function initVideoPlayer() {
    const video = document.getElementById('videoPlayer');
    
    video.addEventListener('loadedmetadata', () => {
        const totalEl = document.getElementById('totalTime');
        if (totalEl) {
            totalEl.textContent = formatTime(video.duration);
        }
        updateStatus(`Video loaded: ${formatTime(video.duration)}`);
    });
    
    video.addEventListener('timeupdate', () => {
        const currentEl = document.getElementById('currentTime');
        if (currentEl) {
            currentEl.textContent = formatTime(video.currentTime);
        }
    });
}

// Initialize timeline
function initTimeline() {
    // Create time ruler markers
    const ruler = document.getElementById('timeRuler');
    if (ruler) {
        for (let i = 0; i <= 60; i += 5) {
            const marker = document.createElement('div');
            marker.style.cssText = `
                position: absolute;
                left: ${i * 20}px;
                top: 0;
                height: 100%;
                border-left: 1px solid #333344;
                padding: 5px;
                font-size: 10px;
                color: #aaaaaa;
            `;
            marker.textContent = i + 's';
            ruler.appendChild(marker);
        }
    }
}

// Event listeners
function initEventListeners() {
    // File upload buttons
    document.querySelectorAll('.tool-btn').forEach(btn => {
        if (btn.textContent.includes('Upload')) {
            btn.addEventListener('click', () => {
                const type = btn.textContent.includes('Video') ? 'video' :
                            btn.textContent.includes('Audio') ? 'audio' : 'image';
                uploadMedia(type);
            });
        }
    });
    
    // Transition buttons
    document.querySelectorAll('.transition-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const effect = btn.getAttribute('data-effect');
            applyTransition(effect);
        });
    });
    
    // AI detection
    document.querySelectorAll('.ai-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (btn.textContent.includes('Detect')) {
                await detectScenes();
            } else if (btn.textContent.includes('Auto Trim')) {
                await autoTrim();
            }
        });
    });
}

// Upload media
function uploadMedia(type) {
    const inputId = type + 'Input';
    const input = document.getElementById(inputId);
    if (input) {
        input.click();
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const url = URL.createObjectURL(file);
                
                if (type === 'video') {
                    const video = document.getElementById('videoPlayer');
                    const overlay = document.getElementById('videoOverlay');
                    
                    video.src = url;
                    video.load();
                    
                    if (overlay) {
                        overlay.style.display = 'none';
                    }
                    
                    updateFileInfo(file.name, file.size);
                    updateStatus(`📹 Video loaded: ${file.name}`);
                    
                    // Store in session
                    if (window.sessionManager?.project) {
                        window.sessionManager.project.videoFile = {
                            name: file.name,
                            size: file.size,
                            type: file.type,
                            url: url
                        };
                        window.sessionManager.save();
                    }
                }
            }
        };
    }
}

// AI Scene Detection
async function detectScenes() {
    const video = document.getElementById('videoPlayer');
    if (!video.src || video.src.startsWith('data:')) {
        updateStatus('Please upload a video first', 'error');
        return;
    }
    
    showLoading('🤖 AI is detecting scenes...');
    
    try {
        const response = await fetch('/api/detect-scenes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                duration: video.duration || 30,
                action: 'detect_scenes'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayScenes(data.scenes);
            updateStatus(`🎬 Found ${data.count} scenes!`, 'success');
        } else {
            updateStatus('Scene detection failed: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('Server error: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display detected scenes
function displayScenes(scenes) {
    const container = document.getElementById('aiResults');
    const list = document.getElementById('scenesList');
    
    if (!container || !list) return;
    
    list.innerHTML = scenes.map(scene => `
        <div class="scene-item" style="
            background: rgba(155, 89, 182, 0.1);
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #9b59b6;
        ">
            <div><strong>${scene.id}</strong></div>
            <div>${scene.start}s → ${scene.end}s (${scene.duration}s)</div>
            <div style="font-size: 12px; color: #aaa;">
                Confidence: ${(scene.confidence * 100).toFixed(0)}% 
                | Transition: ${scene.suggested_transition || 'cut'}
            </div>
        </div>
    `).join('');
    
    container.style.display = 'block';
    window.detectedScenes = scenes;
}

// Apply scenes to timeline
function applyScenes() {
    if (!window.detectedScenes) {
        updateStatus('No scenes to apply', 'error');
        return;
    }
    
    // Here you would add the scenes to the timeline
    updateStatus(`Applied ${window.detectedScenes.length} scenes to timeline`, 'success');
    
    // For now, just show a message
    setTimeout(() => {
        updateStatus('Ready');
    }, 2000);
}

// Save project
async function saveProject() {
    if (!window.sessionManager?.project) {
        updateStatus('No project to save', 'error');
        return;
    }
    
    showLoading('💾 Saving project...');
    
    try {
        const response = await fetch('/api/project/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(window.sessionManager.project)
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateStatus(`✅ Project saved: ${data.project_id}`, 'success');
        } else {
            updateStatus('Save failed: ' + data.error, 'error');
        }
    } catch (error) {
        updateStatus('Save error: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Export project
function exportProject() {
    updateStatus('Export feature coming soon!');
    // Implementation would go here
}

// Video controls
function playVideo() {
    const video = document.getElementById('videoPlayer');
    video.play();
}

function pauseVideo() {
    const video = document.getElementById('videoPlayer');
    video.pause();
}

function stopVideo() {
    const video = document.getElementById('videoPlayer');
    video.pause();
    video.currentTime = 0;
}

// Timeline controls
function addVideoTrack() {
    updateStatus('Added new video track');
    // Implementation would go here
}

function addAudioTrack() {
    updateStatus('Added new audio track');
    // Implementation would go here
}

function zoomIn() {
    const zoomEl = document.getElementById('zoomLevel');
    if (zoomEl) {
        let zoom = parseInt(zoomEl.textContent);
        zoom = Math.min(zoom + 25, 400);
        zoomEl.textContent = zoom + '%';
        updateStatus(`Zoom: ${zoom}%`);
    }
}

function zoomOut() {
    const zoomEl = document.getElementById('zoomLevel');
    if (zoomEl) {
        let zoom = parseInt(zoomEl.textContent);
        zoom = Math.max(zoom - 25, 25);
        zoomEl.textContent = zoom + '%';
        updateStatus(`Zoom: ${zoom}%`);
    }
}

// Apply transition
function applyTransition(effect) {
    const duration = document.getElementById('transitionDuration')?.value || 1;
    updateStatus(`Applied ${effect} transition (${duration}s)`);
}

// Check server health
async function checkServerHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('Server health:', data);
        updateStatus(`Connected to server on port ${data.port}`);
    } catch (error) {
        console.warn('Server not responding:', error);
        updateStatus('⚠️ Running in offline mode', 'warning');
    }
}

// Utility functions
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function updateStatus(message, type = 'info') {
    const el = document.getElementById('statusMessage');
    if (el) {
        el.textContent = message;
        el.style.color = type === 'error' ? '#e74c3c' :
                        type === 'success' ? '#2ecc71' :
                        type === 'warning' ? '#f39c12' : '#ffffff';
    }
    console.log('Status:', message);
}

function updateFileInfo(filename, size) {
    const el = document.getElementById('fileInfo');
    if (el) {
        const sizeMB = (size / 1024 / 1024).toFixed(1);
        el.textContent = `${filename} (${sizeMB}MB)`;
    }
}

function showLoading(message) {
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    
    if (overlay) overlay.style.display = 'flex';
    if (text) text.textContent = message;
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
}