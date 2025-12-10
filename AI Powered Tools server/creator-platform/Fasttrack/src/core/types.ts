// src/core/types.ts
export type MediaType = 'video' | 'audio' | 'image' | 'text' | 'effect';

export interface Position {
    x: number;
    y: number;
}

export interface Size {
    width: number;
    height: number;
}

export interface TimeRange {
    start: number; // in seconds
    end: number;   // in seconds
    duration: number;
}

export interface Filter {
    id: string;
    name: string;
    type: 'color' | 'blur' | 'distortion' | 'transition' | 'audio';
    enabled: boolean;
    parameters: Record<string, any>;
    apply: (context: CanvasRenderingContext2D | AudioContext, progress?: number) => void;
}

export interface Keyframe {
    time: number; // in seconds
    value: any;
    easing?: 'linear' | 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out';
}

export interface Animation {
    property: string;
    keyframes: Keyframe[];
    duration: number;
}

export interface Clip {
    id: string;
    name: string;
    type: MediaType;
    source: string; // URL, blob URL, or file path
    thumbnail?: string;
    
    // Timing
    inPoint: number; // Start time in source (seconds)
    outPoint: number; // End time in source (seconds)
    position: number; // Position on timeline (seconds)
    duration: number; // Calculated: outPoint - inPoint
    
    // Properties
    muted: boolean;
    locked: boolean;
    volume: number; // 0.0 to 1.0
    speed: number; // 1.0 = normal, 0.5 = half speed, 2.0 = double speed
    
    // Transform
    transform: {
        x: number;
        y: number;
        scaleX: number;
        scaleY: number;
        rotation: number;
        opacity: number;
    };
    
    // Effects
    filters: Filter[];
    animations: Animation[];
    
    // Metadata
    metadata: {
        originalDuration: number;
        frameRate: number;
        resolution: Size;
        codec?: string;
        bitrate?: number;
        fileSize?: number;
        createdAt: Date;
        modifiedAt: Date;
    };
    
    // Methods
    getCurrentFrame(time: number): HTMLVideoElement | HTMLAudioElement | HTMLImageElement | null;
    isVisibleAt(time: number): boolean;
    getBoundsAt(time: number): { x: number, y: number, width: number, height: number };
}

export interface Track {
    id: string;
    name: string;
    type: 'video' | 'audio' | 'effect';
    index: number;
    height: number; // in pixels
    
    // State
    muted: boolean;
    locked: boolean;
    visible: boolean;
    solo: boolean;
    
    // Content
    clips: Clip[];
    
    // Properties
    opacity: number;
    volume: number;
    blendMode: 'normal' | 'multiply' | 'screen' | 'overlay';
    
    // Methods
    addClip(clip: Clip): void;
    removeClip(clipId: string): Clip | null;
    getClipAt(time: number): Clip | null;
    getClipsInRange(start: number, end: number): Clip[];
    moveClip(clipId: string, newPosition: number): boolean;
    trimClip(clipId: string, newInPoint: number, newOutPoint: number): boolean;
}

export interface Timeline {
    id: string;
    name: string;
    duration: number; // in seconds
    
    // Tracks
    videoTracks: Track[];
    audioTracks: Track[];
    
    // Properties
    frameRate: number; // fps
    resolution: Size;
    backgroundColor: string;
    
    // Time
    currentTime: number;
    startTime: number;
    endTime: number;
    
    // Playback
    playing: boolean;
    playbackRate: number;
    
    // Methods
    addTrack(type: 'video' | 'audio', index?: number): Track;
    removeTrack(trackId: string): boolean;
    moveTrack(trackId: string, newIndex: number): boolean;
    
    addClipToTrack(trackId: string, clip: Clip): boolean;
    removeClipFromTrack(trackId: string, clipId: string): boolean;
    
    getClipAtPosition(x: number, y: number): { track: Track, clip: Clip } | null;
    getClipsAtTime(time: number): Clip[];
    
    splitClip(trackId: string, clipId: string, splitTime: number): Clip[] | null;
    mergeClips(trackId: string, clipIds: string[]): Clip | null;
    
    renderFrame(time: number): Promise<HTMLCanvasElement>;
    renderAudio(time: number, duration: number): Promise<AudioBuffer>;
}

export interface Project {
    id: string;
    name: string;
    version: string;
    
    // Timeline
    timeline: Timeline;
    
    // Assets
    assets: {
        videos: Map<string, File | Blob>;
        audios: Map<string, File | Blob>;
        images: Map<string, File | Blob>;
        effects: Map<string, any>;
    };
    
    // Settings
    settings: {
        autoSave: boolean;
        autoSaveInterval: number;
        previewQuality: 'low' | 'medium' | 'high';
        renderQuality: 'low' | 'medium' | 'high' | 'ultra';
        defaultFrameRate: number;
        defaultResolution: Size;
    };
    
    // Metadata
    metadata: {
        created: Date;
        modified: Date;
        author: string;
        description: string;
        tags: string[];
    };
    
    // Methods
    addAsset(type: 'video' | 'audio' | 'image', file: File): string;
    removeAsset(assetId: string): boolean;
    getAssetUrl(assetId: string): string | null;
    
    save(): string; // Returns JSON string
    load(data: string): boolean;
    export(format: 'json' | 'xml' | 'ffmpeg'): any;
}