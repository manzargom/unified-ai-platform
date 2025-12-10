// src/core/clip.ts
import { Clip, MediaType, Filter, Animation, Size, Keyframe } from './types';

export class VideoClip implements Clip {
    id: string;
    name: string;
    type: MediaType = 'video';
    source: string;
    thumbnail?: string;
    
    inPoint: number = 0;
    outPoint: number = 0;
    position: number = 0;
    duration: number = 0;
    
    muted: boolean = false;
    locked: boolean = false;
    volume: number = 1.0;
    speed: number = 1.0;
    
    transform = {
        x: 0,
        y: 0,
        scaleX: 1,
        scaleY: 1,
        rotation: 0,
        opacity: 1
    };
    
    filters: Filter[] = [];
    animations: Animation[] = [];
    
    metadata = {
        originalDuration: 0,
        frameRate: 30,
        resolution: { width: 1920, height: 1080 },
        codec: '',
        bitrate: 0,
        fileSize: 0,
        createdAt: new Date(),
        modifiedAt: new Date()
    };
    
    private videoElement: HTMLVideoElement | null = null;
    private canvasCache: Map<number, HTMLCanvasElement> = new Map();
    
    constructor(id: string, name: string, source: string, duration: number) {
        this.id = id;
        this.name = name;
        this.source = source;
        this.outPoint = duration;
        this.duration = duration;
        this.metadata.originalDuration = duration;
        
        this.initializeVideo();
    }
    
    private initializeVideo(): void {
        this.videoElement = document.createElement('video');
        this.videoElement.src = this.source;
        this.videoElement.crossOrigin = 'anonymous';
        this.videoElement.preload = 'metadata';
        
        this.videoElement.addEventListener('loadedmetadata', () => {
            this.metadata.originalDuration = this.videoElement!.duration;
            this.outPoint = Math.min(this.outPoint, this.videoElement!.duration);
            this.duration = this.outPoint - this.inPoint;
            
            // Extract thumbnail
            this.generateThumbnail();
        });
    }
    
    private async generateThumbnail(): Promise<void> {
        if (!this.videoElement) return;
        
        try {
            // Seek to 25% of the clip for thumbnail
            this.videoElement.currentTime = this.duration * 0.25;
            
            await new Promise(resolve => {
                this.videoElement!.addEventListener('seeked', resolve, { once: true });
            });
            
            const canvas = document.createElement('canvas');
            canvas.width = 160;
            canvas.height = 90;
            const ctx = canvas.getContext('2d')!;
            ctx.drawImage(this.videoElement, 0, 0, canvas.width, canvas.height);
            
            this.thumbnail = canvas.toDataURL('image/jpeg', 0.7);
        } catch (error) {
            console.warn('Failed to generate thumbnail:', error);
        }
    }
    
    getCurrentFrame(time: number): HTMLVideoElement | null {
        if (!this.videoElement || !this.isVisibleAt(time)) return null;
        
        const clipTime = time - this.position;
        const sourceTime = this.inPoint + (clipTime * this.speed);
        
        if (sourceTime >= this.inPoint && sourceTime <= this.outPoint) {
            this.videoElement.currentTime = sourceTime;
            return this.videoElement;
        }
        
        return null;
    }
    
    isVisibleAt(time: number): boolean {
        if (this.muted || this.transform.opacity <= 0) return false;
        
        const clipStart = this.position;
        const clipEnd = this.position + this.duration;
        
        return time >= clipStart && time <= clipEnd;
    }
    
    getBoundsAt(time: number): { x: number, y: number, width: number, height: number } {
        const clipTime = time - this.position;
        const progress = clipTime / this.duration;
        
        // Apply animations
        const animatedTransform = this.applyAnimations(progress);
        
        return {
            x: animatedTransform.x,
            y: animatedTransform.y,
            width: this.metadata.resolution.width * animatedTransform.scaleX,
            height: this.metadata.resolution.height * animatedTransform.scaleY
        };
    }
    
    private applyAnimations(progress: number): typeof this.transform {
        const result = { ...this.transform };
        
        this.animations.forEach(animation => {
            if (animation.keyframes.length < 2) return;
            
            // Find surrounding keyframes
            const prevKeyframe = animation.keyframes
                .filter(k => k.time <= progress)
                .pop();
            const nextKeyframe = animation.keyframes
                .filter(k => k.time >= progress)
                .shift();
            
            if (!prevKeyframe || !nextKeyframe) return;
            
            // Calculate interpolation factor
            const t = (progress - prevKeyframe.time) / (nextKeyframe.time - prevKeyframe.time);
            
            // Apply interpolation
            if (typeof prevKeyframe.value === 'number') {
                const value = this.interpolate(
                    prevKeyframe.value,
                    nextKeyframe.value,
                    t,
                    prevKeyframe.easing
                );
                (result as any)[animation.property] = value;
            }
        });
        
        return result;
    }
    
    private interpolate(start: number, end: number, t: number, easing?: string): number {
        t = Math.max(0, Math.min(1, t));
        
        switch (easing) {
            case 'ease-in':
                t = t * t;
                break;
            case 'ease-out':
                t = t * (2 - t);
                break;
            case 'ease-in-out':
                t = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
                break;
            // 'linear' is default
        }
        
        return start + (end - start) * t;
    }
    
    // Factory method for creating clips from files
    static async fromFile(file: File): Promise<VideoClip> {
        const id = `clip_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const url = URL.createObjectURL(file);
        
        // Get video duration
        const duration = await new Promise<number>((resolve) => {
            const video = document.createElement('video');
            video.src = url;
            video.onloadedmetadata = () => {
                resolve(video.duration);
                URL.revokeObjectURL(url);
            };
        });
        
        return new VideoClip(id, file.name, url, duration);
    }
}

// AudioClip class (similar structure)
export class AudioClip implements Clip {
    // Implementation similar to VideoClip but for audio
    // ...
}

// ImageClip class
export class ImageClip implements Clip {
    // Implementation for static images
    // ...
}