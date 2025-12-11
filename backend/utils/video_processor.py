import os
import json
import uuid
from datetime import datetime
import subprocess
from moviepy.editor import VideoFileClip

class VideoProcessor:
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
    
    def extract_clip(self, video_path, start_time, end_time, session_id):
        """Extract clip from video"""
        try:
            # Create clips directory
            clips_dir = f"static/uploads/{session_id}/clips"
            os.makedirs(clips_dir, exist_ok=True)
            
            # Generate unique clip name
            clip_name = f"clip_{int(datetime.now().timestamp())}.mp4"
            clip_path = os.path.join(clips_dir, clip_name)
            
            # Extract clip using moviepy
            with VideoFileClip(video_path) as video:
                clip = video.subclip(start_time, end_time)
                clip.write_videofile(clip_path, codec='libx264', audio_codec='aac')
                clip.close()
            
            # Create web-friendly version
            web_clip_path = clip_path.replace('.mp4', '_web.mp4')
            self.convert_for_web(clip_path, web_clip_path)
            
            return web_clip_path
            
        except Exception as e:
            print(f"Error extracting clip: {e}")
            return None
    
    def convert_for_web(self, input_path, output_path):
        """Convert video for web playback"""
        try:
            command = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k',
                '-movflags', '+faststart',
                '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease',
                '-y', output_path
            ]
            
            subprocess.run(command, check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"Error converting video: {e}")
            return False
    
    def get_video_info(self, video_path):
        """Get video information"""
        try:
            with VideoFileClip(video_path) as video:
                duration = video.duration
                size = video.size  # (width, height)
                fps = video.fps
                
                # Get file size
                file_size = os.path.getsize(video_path)
                
                return {
                    'duration': duration,
                    'width': size[0],
                    'height': size[1],
                    'resolution': f"{size[0]}x{size[1]}",
                    'fps': fps,
                    'file_size': file_size
                }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    def validate_video(self, file_path):
        """Validate video file"""
        if not os.path.exists(file_path):
            return False
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.supported_formats:
            return False
        
        try:
            with VideoFileClip(file_path) as video:
                if video.duration <= 0:
                    return False
            return True
        except:
            return False