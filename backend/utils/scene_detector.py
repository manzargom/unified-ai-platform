import cv2
import numpy as np
import os
from datetime import datetime

class SceneDetector:
    def __init__(self, threshold=30.0, min_scene_length=1.0):
        self.threshold = threshold  # Pixel difference threshold
        self.min_scene_length = min_scene_length  # Minimum scene length in seconds
        self.use_framepack = self.check_framepack()
    
    def check_framepack(self):
        """Check if FramePack is available"""
        try:
            # Try to import FramePack
            import importlib.util
            spec = importlib.util.find_spec("framepack")
            return spec is not None
        except:
            return False
    
    def detect(self, video_path):
        """Detect scenes in video using best available method"""
        if self.use_framepack:
            return self.detect_with_framepack(video_path)
        else:
            return self.detect_with_opencv(video_path)
    
    def detect_with_opencv(self, video_path):
        """Detect scenes using OpenCV (fallback method)"""
        scenes = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return scenes
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if fps == 0 or total_frames == 0:
                return scenes
            
            prev_frame = None
            scene_start = 0
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_time = frame_count / fps
                
                # Convert to grayscale for comparison
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate difference between frames
                    diff = cv2.absdiff(prev_frame, gray)
                    diff_value = np.mean(diff)
                    
                    # If difference exceeds threshold, it's a new scene
                    if diff_value > self.threshold:
                        scene_end = current_time
                        scene_duration = scene_end - scene_start
                        
                        if scene_duration >= self.min_scene_length:
                            scenes.append({
                                'start': scene_start,
                                'end': scene_end,
                                'duration': scene_duration,
                                'frame': frame_count
                            })
                        
                        scene_start = current_time
                
                prev_frame = gray
                frame_count += 1
            
            # Add final scene
            if scene_start < (total_frames / fps):
                scenes.append({
                    'start': scene_start,
                    'end': total_frames / fps,
                    'duration': (total_frames / fps) - scene_start,
                    'frame': frame_count
                })
            
            cap.release()
            
            # Merge very short scenes
            scenes = self.merge_short_scenes(scenes)
            
            return scenes
            
        except Exception as e:
            print(f"Error detecting scenes: {e}")
            return []
    
    def detect_with_framepack(self, video_path):
        """Detect scenes using FramePack (superior method)"""
        try:
            from framepack import ShotDetector
            
            detector = ShotDetector()
            shots = detector.detect(video_path)
            
            scenes = []
            for shot in shots:
                scenes.append({
                    'start': shot.start_time,
                    'end': shot.end_time,
                    'duration': shot.end_time - shot.start_time,
                    'frame': shot.middle_frame,
                    'type': shot.scene_type if hasattr(shot, 'scene_type') else 'unknown',
                    'confidence': shot.confidence if hasattr(shot, 'confidence') else 1.0
                })
            
            return scenes
            
        except Exception as e:
            print(f"FramePack detection failed, falling back: {e}")
            return self.detect_with_opencv(video_path)
    
    def merge_short_scenes(self, scenes, min_duration=1.5):
        """Merge scenes that are too short"""
        if not scenes:
            return []
        
        merged = []
        current_scene = scenes[0].copy()
        
        for scene in scenes[1:]:
            if scene['duration'] < min_duration:
                # Merge with current scene
                current_scene['end'] = scene['end']
                current_scene['duration'] = current_scene['end'] - current_scene['start']
            else:
                merged.append(current_scene)
                current_scene = scene.copy()
        
        merged.append(current_scene)
        return merged
    
    def extract_keyframes(self, video_path, scenes, output_dir):
        """Extract keyframes for each scene"""
        keyframes = []
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            cap = cv2.VideoCapture(video_path)
            
            for i, scene in enumerate(scenes):
                # Get middle frame of scene
                middle_time = (scene['start'] + scene['end']) / 2
                cap.set(cv2.CAP_PROP_POS_MSEC, middle_time * 1000)
                ret, frame = cap.read()
                
                if ret:
                    keyframe_path = os.path.join(output_dir, f"scene_{i+1:03d}.jpg")
                    cv2.imwrite(keyframe_path, frame)
                    
                    keyframes.append({
                        'scene_index': i,
                        'time': middle_time,
                        'path': keyframe_path
                    })
            
            cap.release()
            return keyframes
            
        except Exception as e:
            print(f"Error extracting keyframes: {e}")
            return []