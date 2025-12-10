class VideoEditor {
    constructor() {
        this.sessionId = null;
        this.currentVideo = null;
        this.videos = [];
        this.timelineData = { videoTrack: [], audioTrack: [] };
        this.isDragging = false;
        this.draggingType = null;
        this.timelinePlaying = false;
        this.currentClipIndex = 0;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupDualSlider();
        this.updateSessionInfo();
        this.loadTimelineState();
    }

    setupEventListeners() {
        // File input
        document.getElementById('file-input').addEventListener('change', (e) => this.handleFiles(e.target.files));
        
        // Video events
        const video = document.getElementById('main-video');
        video.addEventListener('loadedmetadata', () => this.updateDualSlider(video));
        video.addEventListener('ended', () => this.onVideoEnded(video));
        
        // Buttons
        document.getElementById('play-selection').addEventListener('click', () => this.playSelection(video));
        document.getElementById('add-clip').addEventListener('click', () => this.addClipToTimeline());
        document.getElementById('play-timeline').addEventListener('click', () => this.playTimeline(video));
        document.getElementById('clear-timeline').addEventListener('click', () => this.clearTimeline());
        document.getElementById('export-timeline').addEventListener('click', () => this.exportTimeline());
        
        // Navbar buttons
        document.getElementById('save-project')?.addEventListener('click', () => this.saveProject());
        document.getElementById('export-video')?.addEventListener('click', () => this.exportVideo());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e, video));
        
        // Initialize
        this.updateVideosList();
        this.updateTimelineInfo();
    }

    setupDragAndDrop() {
        const dropZone = document.getElementById('drop-zone');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            });
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            });
        });
        
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            this.handleFiles(files);
        });
    }

    setupDualSlider() {
        const track = document.getElementById('slider-track');
        const startThumb = document.getElementById('start-thumb');
        const endThumb = document.getElementById('end-thumb');
        const selectedRange = document.getElementById('selected-range');
        
        // Initialize positions
        startThumb.style.left = '0%';
        endThumb.style.left = '100%';
        selectedRange.style.left = '0%';
        selectedRange.style.width = '100%';
        
        // Setup dragging with proper isolation
        const setupThumbDrag = (thumb, type) => {
            thumb.addEventListener('mousedown', (e) => {
                this.isDragging = true;
                this.draggingType = type;
                
                const onMouseMove = (moveEvent) => {
                    if (!this.isDragging) return;
                    
                    const rect = track.getBoundingClientRect();
                    let percent = ((moveEvent.clientX - rect.left) / rect.width) * 100;
                    percent = Math.max(0, Math.min(100, percent));
                    
                    // Don't let thumbs get too close (1% gap)
                    const otherType = type === 'start' ? 'end' : 'start';
                    const otherThumb = type === 'start' ? endThumb : startThumb;
                    const otherPercent = parseFloat(otherThumb.style.left);
                    
                    if (type === 'start' && percent >= otherPercent - 1) {
                        percent = otherPercent - 1;
                    }
                    if (type === 'end' && percent <= otherPercent + 1) {
                        percent = otherPercent + 1;
                    }
                    
                    this.updateThumbPosition(type, percent, false);
                };
                
                const onMouseUp = () => {
                    this.isDragging = false;
                    this.draggingType = null;
                    document.removeEventListener('mousemove', onMouseMove);
                    document.removeEventListener('mouseup', onMouseUp);
                };
                
                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
                e.preventDefault();
            });
        };
        
        setupThumbDrag(startThumb, 'start');
        setupThumbDrag(endThumb, 'end');
        
        // Click on track to move start thumb
        track.addEventListener('click', (e) => {
            if (this.isDragging) return;
            const rect = track.getBoundingClientRect();
            const percent = ((e.clientX - rect.left) / rect.width) * 100;
            this.updateThumbPosition('start', percent, true);
        });
        
        // Store references
        this.sliderElements = { track, startThumb, endThumb, selectedRange };
    }

    updateThumbPosition(type, percent, updateVideo = true) {
        const video = document.getElementById('main-video');
        if (!video || !video.duration) return;
        
        // Update the specific thumb
        this.sliderElements[type + 'Thumb'].style.left = `${percent}%`;
        
        // Get current positions
        const startPercent = parseFloat(this.sliderElements.startThumb.style.left);
        const endPercent = parseFloat(this.sliderElements.endThumb.style.left);
        
        // Update selected range
        const left = Math.min(startPercent, endPercent);
        const width = Math.abs(endPercent - startPercent);
        
        this.sliderElements.selectedRange.style.left = `${left}%`;
        this.sliderElements.selectedRange.style.width = `${width}%`;
        
        // Update labels
        const startTime = (startPercent / 100) * video.duration;
        const endTime = (endPercent / 100) * video.duration;
        const duration = endTime - startTime;
        
        document.getElementById('start-label').textContent = this.formatTime(startTime);
        document.getElementById('end-label').textContent = this.formatTime(endTime);
        document.getElementById('duration-label').textContent = this.formatTime(duration);
        document.getElementById('clip-duration').textContent = this.formatTime(duration);
        
        // Move video to thumb position if requested
        if (updateVideo) {
            const timeToSet = type === 'start' ? startTime : endTime;
            video.currentTime = timeToSet;
        }
    }

    adjustBothThumbs(direction) {
        const video = document.getElementById('main-video');
        if (!video.duration) return;
        
        const step = 0.5; // 0.5 second steps
        const startPercent = parseFloat(this.sliderElements.startThumb.style.left);
        const endPercent = parseFloat(this.sliderElements.endThumb.style.left);
        
        // Calculate new positions
        let newStartPercent = startPercent + (direction * step / video.duration * 100);
        let newEndPercent = endPercent + (direction * step / video.duration * 100);
        
        // Keep within bounds
        newStartPercent = Math.max(0, Math.min(100, newStartPercent));
        newEndPercent = Math.max(0, Math.min(100, newEndPercent));
        
        // Keep minimum gap
        if (newStartPercent >= newEndPercent - 1) {
            newStartPercent = newEndPercent - 1;
        }
        
        // Update both thumbs
        this.updateThumbPosition('start', newStartPercent, false);
        this.updateThumbPosition('end', newEndPercent, false);
    }

    handleKeyboardShortcuts(e, video) {
        if (!video.duration) return;
        
        // A/Left or D/Right: Move both sliders
        if (e.code === 'KeyA' || e.code === 'ArrowLeft') {
            e.preventDefault();
            const step = e.shiftKey ? 0.1 : (e.ctrlKey ? 2 : 0.5);
            this.adjustBothThumbs(-step);
        }
        if (e.code === 'KeyD' || e.code === 'ArrowRight') {
            e.preventDefault();
            const step = e.shiftKey ? 0.1 : (e.ctrlKey ? 2 : 0.5);
            this.adjustBothThumbs(step);
        }
        
        // Space: Play/Pause
        if (e.code === 'Space' && document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            if (video.paused) {
                video.play();
            } else {
                video.pause();
            }
        }
    }

    updateDualSlider(video) {
        if (!video.duration) return;
        
        this.sliderElements.startThumb.style.left = '0%';
        this.sliderElements.endThumb.style.left = '100%';
        this.sliderElements.selectedRange.style.left = '0%';
        this.sliderElements.selectedRange.style.width = '100%';
        
        document.getElementById('start-label').textContent = '00:00';
        document.getElementById('end-label').textContent = this.formatTime(video.duration);
        document.getElementById('duration-label').textContent = this.formatTime(video.duration);
        document.getElementById('clip-duration').textContent = this.formatTime(video.duration);
    }

    async handleFiles(files) {
        if (!files.length) return;

        if (!this.sessionId) {
            this.sessionId = 'session_' + Date.now();
            this.updateSessionInfo();
        }

        for (const file of files) {
            const progressContainer = document.getElementById('upload-progress');
            const progressBar = document.getElementById('progress-bar');
            const progressText = document.getElementById('progress-text');
            
            progressContainer.style.display = 'block';
            progressBar.style.width = '30%';
            progressText.textContent = `Uploading: ${file.name}`;
            this.showStatus(`Uploading: ${file.name}`, 'info');

            // Check file type
            const fileExt = '.' + file.name.split('.').pop().toLowerCase();
            const isImage = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'].includes(fileExt);
            const isVideo = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv'].includes(fileExt);
            
            if (!isImage && !isVideo) {
                this.showStatus(`Skipped: ${file.name} (unsupported)`, 'warning');
                continue;
            }

            const formData = new FormData();
            formData.append('file', file);
            formData.append('is_image', isImage.toString());

            try {
                const response = await fetch('/api/upload', { 
                    method: 'POST', 
                    body: formData 
                });
                const data = await response.json();

                if (data.success) {
                    data.type = isImage ? 'image' : 'video';
                    
                    this.videos.push(data);
                    
                    // Auto-switch to first video (not image)
                    if (this.videos.length === 1 && !isImage) {
                        this.switchVideo(0);
                    }
                    
                    progressBar.style.width = '100%';
                    progressText.textContent = 'Complete!';
                    
                    setTimeout(() => {
                        progressContainer.style.display = 'none';
                        progressBar.style.width = '0%';
                    }, 500);
                    
                    this.showStatus(`✓ ${file.name} uploaded`, 'success');
                    this.updateVideosList();
                }
            } catch (error) {
                progressContainer.style.display = 'none';
                this.showStatus(`Upload failed: ${file.name}`, 'error');
            }
        }
    }

    switchVideo(index) {
        if (index < 0 || index >= this.videos.length) return;
        
        const video = document.getElementById('main-video');
        const newVideo = this.videos[index];
        
        // Only switch if it's a video (not an image)
        if (newVideo.type === 'image') {
            this.showStatus(`Cannot play image: ${newVideo.original_filename}`, 'info');
            return;
        }
        
        // Store current state
        const wasPlaying = !video.paused;
        const currentTime = video.currentTime;
        
        // Switch video
        this.currentVideo = newVideo;
        video.src = newVideo.cached_path;
        video.load();
        
        video.onloadeddata = () => {
            this.updateVideoInfoDisplay(newVideo);
            this.updateDualSlider(video);
            this.updateVideosList();
            
            // Try to restore playback state
            const newTime = Math.min(currentTime, video.duration);
            video.currentTime = newTime;
            
            if (wasPlaying) {
                setTimeout(() => video.play().catch(() => {}), 100);
            }
            
            this.showStatus(`Now playing: ${newVideo.original_filename}`, 'info');
        };
        
        video.onerror = () => {
            this.showStatus(`Error loading: ${newVideo.original_filename}`, 'error');
        };
    }

    updateVideoInfoDisplay(videoData) {
        const container = document.getElementById('video-info');
        
        if (!videoData || !videoData.original_filename) {
            container.innerHTML = '<p class="text-muted mb-0 small">No video loaded</p>';
            return;
        }
        
        const isImage = videoData.type === 'image';
        
        container.innerHTML = `
            <div class="mb-2">
                <div class="small text-muted">File:</div>
                <div class="compact-filename" title="${videoData.original_filename}">
                    ${videoData.original_filename}
                </div>
                <span class="badge ${isImage ? 'bg-warning' : 'bg-info'}">${isImage ? 'Image' : 'Video'}</span>
            </div>
            <div class="mb-2">
                <div class="small text-muted">${isImage ? 'Resolution:' : 'Duration:'}</div>
                <div>${isImage ? videoData.resolution : this.formatTime(videoData.duration)}</div>
            </div>
            <div class="mb-2">
                <div class="small text-muted">Size:</div>
                <div>${this.formatFileSize(videoData.file_size)}</div>
            </div>
            ${isImage ? '' : `
            <div class="mb-0">
                <div class="small text-muted">Format:</div>
                <div>${videoData.original_filename.split('.').pop().toUpperCase()}</div>
            </div>
            `}
        `;
    }

    playSelection(video) {
        if (!video.duration) {
            this.showStatus('No video loaded', 'warning');
            return;
        }
        
        const startPercent = parseFloat(this.sliderElements.startThumb.style.left) / 100;
        const endPercent = parseFloat(this.sliderElements.endThumb.style.left) / 100;
        const startTime = startPercent * video.duration;
        const endTime = endPercent * video.duration;
        
        if (startTime >= endTime) {
            this.showStatus('Invalid selection', 'error');
            return;
        }
        
        video.currentTime = startTime;
        video.play();
        
        this.playInterval = setInterval(() => {
            if (video.currentTime >= endTime || video.paused) {
                video.pause();
                clearInterval(this.playInterval);
            }
        }, 100);
        
        this.showStatus('Playing selected clip', 'info');
    }

    addClipToTimeline() {
        const video = document.getElementById('main-video');
        if (!video.duration) {
            this.showStatus('No video loaded', 'warning');
            return;
        }
        
        const startPercent = parseFloat(this.sliderElements.startThumb.style.left) / 100;
        const endPercent = parseFloat(this.sliderElements.endThumb.style.left) / 100;
        const startTime = startPercent * video.duration;
        const endTime = endPercent * video.duration;
        
        if (startTime >= endTime) {
            this.showStatus('Invalid clip range', 'error');
            return;
        }
        
        const clipNumber = this.timelineData.videoTrack.length + 1;
        
        this.timelineData.videoTrack.push({
            id: Date.now() + Math.random(),
            start: startTime,
            end: endTime,
            name: `Clip ${clipNumber}`,
            duration: endTime - startTime,
            sourceVideo: this.currentVideo?.original_filename || 'Unknown'
        });
        
        this.updateTimelineDisplay();
        this.updateTimelineInfo();
        this.saveTimelineState();
        this.showStatus('Clip added to timeline', 'success');
    }

    updateTimelineDisplay() {
        const container = document.getElementById('video-track');
        container.innerHTML = '';
        
        this.timelineData.videoTrack.forEach((clip, index) => {
            const clipElement = document.createElement('div');
            const clipWidth = Math.max(clip.duration * 3, 60);
            
            clipElement.className = 'clip-item';
            clipElement.style.width = `${clipWidth}px`;
            clipElement.innerHTML = `
                <div class="clip-info">
                    ${clip.name}<br>
                    ${this.formatTime(clip.start)}
                </div>
                <div class="clip-duration">
                    ${this.formatTime(clip.duration)}
                </div>
                <div style="position:absolute;top:2px;right:2px;">
                    <button class="btn btn-sm p-0" onclick="videoEditor.removeClip(${index})" style="font-size:9px;line-height:1;">
                        <i class="bi bi-x text-danger"></i>
                    </button>
                </div>
            `;
            
            clipElement.addEventListener('click', () => {
                const video = document.getElementById('main-video');
                video.currentTime = clip.start;
                // Update sliders to match this clip
                const startPercent = (clip.start / video.duration) * 100;
                const endPercent = (clip.end / video.duration) * 100;
                this.updateThumbPosition('start', startPercent, false);
                this.updateThumbPosition('end', endPercent, false);
            });
            
            container.appendChild(clipElement);
        });
    }

    removeClip(index) {
        this.timelineData.videoTrack.splice(index, 1);
        this.updateTimelineDisplay();
        this.updateTimelineInfo();
        this.saveTimelineState();
        this.showStatus('Clip removed', 'warning');
    }

    clearTimeline() {
        if (confirm('Clear entire timeline?')) {
            this.timelineData = { videoTrack: [], audioTrack: [] };
            this.updateTimelineDisplay();
            this.updateTimelineInfo();
            this.saveTimelineState();
            this.showStatus('Timeline cleared', 'warning');
        }
    }

    onVideoEnded(video) {
        if (this.timelinePlaying) {
            this.playNextClip(video);
        }
    }

    playNextClip(video) {
        this.currentClipIndex++;
        
        if (this.currentClipIndex >= this.timelineData.videoTrack.length) {
            // Finished all clips
            this.timelinePlaying = false;
            this.currentClipIndex = 0;
            this.showStatus('Timeline playback complete', 'success');
            return;
        }
        
        const clip = this.timelineData.videoTrack[this.currentClipIndex];
        video.currentTime = clip.start;
        video.play();
        
        this.showStatus(`Playing clip ${this.currentClipIndex + 1} of ${this.timelineData.videoTrack.length}`, 'info');
    }

    playTimeline(video) {
        if (this.timelineData.videoTrack.length === 0) {
            this.showStatus('Timeline is empty', 'warning');
            return;
        }
        
        this.timelinePlaying = true;
        this.currentClipIndex = 0;
        
        const firstClip = this.timelineData.videoTrack[0];
        video.currentTime = firstClip.start;
        video.play();
        
        this.showStatus(`Playing timeline (${this.timelineData.videoTrack.length} clips)`, 'info');
    }

    updateVideosList() {
        const container = document.getElementById('videos-list');
        container.innerHTML = '';

        if (this.videos.length === 0) {
            container.innerHTML = '<p class="text-muted small text-center mb-0">No files</p>';
            return;
        }

        this.videos.forEach((file, index) => {
            const isActive = this.currentVideo && file.cached_path === this.currentVideo.cached_path;
            const isImage = file.type === 'image';
            const item = document.createElement('div');
            
            item.className = `compact-video-item ${isActive ? 'active' : ''}`;
            item.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi ${isImage ? 'bi-image' : 'bi-play-circle'} me-2 ${isActive ? 'text-success' : (isImage ? 'text-warning' : 'text-primary')}" style="font-size:14px;"></i>
                    <div class="flex-grow-1">
                        <div class="compact-filename" title="${file.original_filename}">
                            ${file.original_filename}
                        </div>
                        <div class="text-muted" style="font-size:10px;">
                            ${isImage ? `${file.resolution} • ${this.formatFileSize(file.file_size)}` : 
                                      `${this.formatTime(file.duration)} • ${this.formatFileSize(file.file_size)}`}
                        </div>
                    </div>
                </div>
            `;
            
            item.addEventListener('click', () => this.switchVideo(index));
            container.appendChild(item);
        });
    }

    updateTimelineInfo() {
        document.getElementById('clip-count').textContent = this.timelineData.videoTrack.length;
        
        let totalDuration = 0;
        this.timelineData.videoTrack.forEach(clip => {
            totalDuration += clip.duration;
        });
        
        document.getElementById('total-duration').textContent = this.formatTime(totalDuration);
    }

    updateSessionInfo() {
        const element = document.getElementById('session-id');
        if (element) {
            element.textContent = this.sessionId ? this.sessionId.substring(0, 8) + '...' : 'New';
        }
    }

    showStatus(message, type = 'info') {
        const statusElement = document.getElementById('status-message');
        if (!statusElement) return;
        
        const icons = { info: 'bi-info-circle', success: 'bi-check-circle', warning: 'bi-exclamation-triangle', error: 'bi-x-circle' };
        const colors = { info: 'text-info', success: 'text-success', warning: 'text-warning', error: 'text-danger' };
        
        statusElement.innerHTML = `<i class="bi ${icons[type]} ${colors[type]}"></i> ${message}`;
        
        if (type === 'success') {
            setTimeout(() => {
                if (statusElement.innerHTML.includes(message)) {
                    statusElement.innerHTML = '<i class="bi bi-info-circle"></i> Ready';
                }
            }, 3000);
        }
    }

    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '00:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    saveTimelineState() {
        const state = {
            videos: this.videos,
            currentVideo: this.currentVideo,
            timelineData: this.timelineData,
            sessionId: this.sessionId
        };
        localStorage.setItem('videoEditorState', JSON.stringify(state));
    }

    loadTimelineState() {
        const saved = localStorage.getItem('videoEditorState');
        if (saved) {
            try {
                const state = JSON.parse(saved);
                this.videos = state.videos || [];
                this.currentVideo = state.currentVideo || null;
                this.timelineData = state.timelineData || { videoTrack: [], audioTrack: [] };
                this.sessionId = state.sessionId || null;
                
                if (this.currentVideo && this.currentVideo.type === 'video') {
                    const video = document.getElementById('main-video');
                    video.src = this.currentVideo.cached_path;
                    video.load();
                    
                    video.onloadeddata = () => {
                        this.updateVideoInfoDisplay(this.currentVideo);
                        this.updateDualSlider(video);
                    };
                }
                
                this.updateTimelineDisplay();
                this.updateTimelineInfo();
                this.updateVideosList();
                this.updateSessionInfo();
                
                this.showStatus('Session restored', 'success');
            } catch (e) {
                console.error('Load error:', e);
            }
        }
    }

    saveProject() {
        this.showStatus('Project saved', 'success');
    }

    exportVideo() {
        this.showStatus('Export started...', 'info');
    }

    exportTimeline() {
        this.showStatus('Exporting timeline...', 'info');
    }
}

// Create global instance
window.videoEditor = new VideoEditor();