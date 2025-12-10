class Timeline {
    constructor() {
        this.tracks = {
            video: [{id: 'v1', clips: []}],
            audio: [{id: 'a1', clips: []}]
        };
        this.nextTrackId = {
            video: 2,
            audio: 2
        };
    }
    
    addTrack(type) {
        const id = type === 'video' ? `v${this.nextTrackId.video++}` : `a${this.nextTrackId.audio++}`;
        this.tracks[type === 'video' ? 'video' : 'audio'].push({
            id: id,
            clips: []
        });
        this.render();
    }
    
    addClip(trackId, clip) {
        // Find track and add clip
        for (const type in this.tracks) {
            for (const track of this.tracks[type]) {
                if (track.id === trackId) {
                    track.clips.push(clip);
                    break;
                }
            }
        }
        this.render();
    }
    
    render() {
        const container = document.getElementById('tracksContainer');
        container.innerHTML = '';
        
        // Render video tracks
        this.tracks.video.forEach(track => {
            const trackElement = this.createTrackElement(track, 'video');
            container.appendChild(trackElement);
        });
        
        // Render audio tracks
        this.tracks.audio.forEach(track => {
            const trackElement = this.createTrackElement(track, 'audio');
            container.appendChild(trackElement);
        });
    }
    
    createTrackElement(track, type) {
        const div = document.createElement('div');
        div.className = `track ${type}-track`;
        div.setAttribute('data-track-id', track.id);
        
        div.innerHTML = `
            <div class="track-label">${track.id.toUpperCase()}</div>
            <div class="track-content" data-track-type="${type}">
                ${track.clips.map(clip => 
                    `<div class="clip" style="left: ${clip.start}px; width: ${clip.duration}px;">
                        ${clip.name}
                    </div>`
                ).join('')}
            </div>
        `;
        
        return div;
    }
}

// Global timeline instance
const timeline = new Timeline();

// Export functions
window.addTrack = (type) => {
    timeline.addTrack(type);
};

window.applyScenes = () => {
    // Apply detected scenes to timeline
    console.log('Applying scenes to timeline');
};