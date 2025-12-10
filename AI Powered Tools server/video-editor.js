// In handleFiles method, after upload:
async handleFiles(files) {
    // ... existing code ...
    
    const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    
    if (data.success) {
        // Store both proxy and original info
        const videoData = {
            ...data.proxy,  // Proxy file for editing
            original_info: data.original_info,  // Original reference
            session_id: data.session_id
        };
        
        this.videos.push(videoData);
        
        // Show proxy info
        this.showStatus(`✓ Created proxy: ${data.proxy.size_mb}MB (Original: ${data.original_info.size_mb}MB)`, 'success');
        
        // Switch to proxy video
        if (this.videos.length === 1) {
            this.switchVideo(0);
        }
        
        this.updateVideosList();
    }
}

// Update video info display to show proxy status
updateVideoInfoDisplay(videoData) {
    const container = document.getElementById('video-info');
    
    if (!videoData || !videoData.original_filename) {
        container.innerHTML = '<p class="text-muted mb-0 small">No video loaded</p>';
        return;
    }
    
    const isProxy = videoData.is_proxy === true;
    
    container.innerHTML = `
        <div class="mb-2">
            <div class="small text-muted">File:</div>
            <div class="compact-filename" title="${videoData.original_filename}">
                ${videoData.original_filename}
            </div>
            ${isProxy ? '<span class="badge bg-info">Proxy</span>' : ''}
        </div>
        ${isProxy ? `
        <div class="mb-2">
            <div class="small text-muted">Proxy Size:</div>
            <div>${videoData.size_mb} MB <span class="text-muted">(Lightweight for editing)</span></div>
        </div>
        ` : ''}
        <div class="mb-2">
            <div class="small text-muted">Duration:</div>
            <div>${this.formatTime(videoData.duration)}</div>
        </div>
        <div class="mb-2">
            <div class="small text-muted">Resolution:</div>
            <div>${videoData.resolution}</div>
        </div>
        ${videoData.original_info ? `
        <div class="mb-0">
            <div class="small text-muted">Original:</div>
            <div>${videoData.original_info.size_mb} MB <span class="text-muted">(Full quality for export)</span></div>
        </div>
        ` : ''}
    `;
}