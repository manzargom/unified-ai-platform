import os
import json
import subprocess
import hashlib
from datetime import datetime
import shutil

class ProxyManager:
    def __init__(self, proxy_dir):
        self.proxy_dir = proxy_dir
        os.makedirs(proxy_dir, exist_ok=True)
    
    def create_proxy(self, original_path, session_id, filename):
        """Create lightweight proxy for editing"""
        
        # Generate unique proxy filename
        file_hash = self.get_file_hash(original_path)
        proxy_filename = f"proxy_{session_id}_{file_hash}.mp4"
        proxy_path = os.path.join(self.proxy_dir, proxy_filename)
        
        # Check if proxy already exists
        if os.path.exists(proxy_path):
            return self.get_proxy_info(proxy_path, session_id, filename)
        
        # Create proxy with optimal settings for editing
        command = [
            'ffmpeg', '-i', original_path,
            '-c:v', 'libx264', '-preset', 'ultrafast',
            '-crf', '28',           # Higher compression
            '-vf', 'scale=960:-2',  # 960p proxy (good balance)
            '-r', '15',             # 15fps (enough for editing)
            '-c:a', 'aac', '-b:a', '64k',  # Low audio quality
            '-movflags', '+faststart',
            '-threads', '2',        # Use 2 threads max
            '-y', proxy_path
        ]
        
        try:
            print(f"Creating proxy: {original_path} -> {proxy_path}")
            result = subprocess.run(command, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return self.get_proxy_info(proxy_path, session_id, filename)
            else:
                print(f"Proxy creation failed: {result.stderr}")
                # Fallback: copy original but smaller
                return self.create_fallback_proxy(original_path, session_id, filename)
                
        except subprocess.TimeoutExpired:
            print("Proxy creation timeout")
            return self.create_fallback_proxy(original_path, session_id, filename)
    
    def create_fallback_proxy(self, original_path, session_id, filename):
        """Create super simple proxy as fallback"""
        file_hash = self.get_file_hash(original_path)
        proxy_filename = f"fallback_{session_id}_{file_hash}.mp4"
        proxy_path = os.path.join(self.proxy_dir, proxy_filename)
        
        command = [
            'ffmpeg', '-i', original_path,
            '-c:v', 'libx264', '-preset', 'superfast',
            '-crf', '32',           # Very high compression
            '-vf', 'scale=480:-2',  # 480p
            '-r', '10',             # 10fps
            '-c:a', 'aac', '-b:a', '32k',
            '-y', proxy_path
        ]
        
        subprocess.run(command, capture_output=True)
        return self.get_proxy_info(proxy_path, session_id, filename)
    
    def get_proxy_info(self, proxy_path, session_id, original_filename):
        """Get proxy file information"""
        if not os.path.exists(proxy_path):
            return None
        
        # Get proxy video info
        info_cmd = [
            'ffprobe', '-v', 'quiet',
            '-show_format', '-show_streams',
            '-print_format', 'json', proxy_path
        ]
        
        result = subprocess.run(info_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None
        
        data = json.loads(result.stdout)
        
        # Find video stream
        video_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
        
        return {
            'original_filename': original_filename,
            'proxy_path': proxy_path,
            'proxy_url': f"/static/proxies/{os.path.basename(proxy_path)}",
            'size': os.path.getsize(proxy_path),
            'size_mb': round(os.path.getsize(proxy_path) / (1024 * 1024), 2),
            'duration': float(data['format'].get('duration', 0)),
            'resolution': f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}" if video_stream else "Unknown",
            'is_proxy': True,
            'proxy_quality': 'standard' if 'fallback' not in proxy_path else 'low'
        }
    
    def get_file_hash(self, file_path):
        """Generate hash for file"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    
    def cleanup_old_proxies(self, max_age_hours=24):
        """Delete proxies older than specified hours"""
        now = datetime.now()
        deleted_count = 0
        
        for proxy_file in os.listdir(self.proxy_dir):
            proxy_path = os.path.join(self.proxy_dir, proxy_file)
            if os.path.isfile(proxy_path):
                file_age = datetime.fromtimestamp(os.path.getmtime(proxy_path))
                age_hours = (now - file_age).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    os.remove(proxy_path)
                    deleted_count += 1
        
        return deleted_count