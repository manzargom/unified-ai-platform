import os
import json
import hashlib
from datetime import datetime, timedelta
import shutil
import subprocess

class CacheManager:
    def __init__(self, cache_dir, max_size_gb=10):
        self.cache_dir = cache_dir
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        self.cache_index = self.load_cache_index()
    
    def load_cache_index(self):
        """Load cache index from file"""
        index_file = os.path.join(self.cache_dir, 'cache_index.json')
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache_index(self):
        """Save cache index to file"""
        index_file = os.path.join(self.cache_dir, 'cache_index.json')
        with open(index_file, 'w') as f:
            json.dump(self.cache_index, f, indent=2)
    
    def get_file_hash(self, file_path):
        """Generate hash for file"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    
    def create_cached_version(self, original_path, session_id):
        """Create cached version of video for web playback"""
        # Generate cache key
        file_hash = self.get_file_hash(original_path)
        cache_key = f"{session_id}_{file_hash}"
        
        # Check if already cached
        if cache_key in self.cache_index:
            cached_info = self.cache_index[cache_key]
            if os.path.exists(cached_info['path']):
                cached_info['last_accessed'] = datetime.now().isoformat()
                self.save_cache_index()
                return cached_info
        
        # Create cached version
        cached_filename = f"{cache_key}.cached.mp4"
        cached_path = os.path.join(self.cache_dir, cached_filename)
        
        # Convert video for web
        self.convert_for_web(original_path, cached_path)
        
        # Get video info
        video_info = self.get_video_info(cached_path)
        
        # Update cache index
        cached_info = {
            'original_path': original_path,
            'path': cached_path,
            'web_path': f"/static/uploads/cache/{cached_filename}",
            'session_id': session_id,
            'file_hash': file_hash,
            'created': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'size': os.path.getsize(cached_path),
            'duration': video_info['duration'],
            'resolution': video_info['resolution'],
            'file_size': video_info['file_size']
        }
        
        self.cache_index[cache_key] = cached_info
        self.save_cache_index()
        
        # Cleanup old cache if needed
        self.cleanup_cache()
        
        return cached_info
    
    def convert_for_web(self, input_path, output_path):
        """Convert video to web-friendly format"""
        try:
            ext = os.path.splitext(input_path)[1].lower()
            
            # For ALL formats, use re-encoding (simpler and more compatible)
            command = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k',
                '-movflags', '+faststart',
                '-vf', 'scale=-2:720',
                '-y', output_path
            ]
            
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=300)
            return True
            
        except Exception as e:
            print(f"Conversion error: {e}")
            # Fallback to original file
            shutil.copy2(input_path, output_path)
            return False
    
    def get_video_info(self, video_path):
        """Get video information quickly without full processing"""
        try:
            command = [
                'ffprobe', '-v', 'quiet', '-show_format',
                '-show_streams', '-print_format', 'json', video_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return None
            
            data = json.loads(result.stdout)
            
            # Find video stream
            video_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if video_stream:
                duration = float(data['format'].get('duration', 0))
                width = int(video_stream.get('width', 0))
                height = int(video_stream.get('height', 0))
                file_size = int(data['format'].get('size', 0))
                
                return {
                    'duration': duration,
                    'width': width,
                    'height': height,
                    'resolution': f"{width}x{height}",
                    'file_size': file_size
                }
            return None
            
        except Exception as e:
            print(f"Quick video info error: {e}")
            return None
    
    def cleanup_cache(self):
        """Remove old cache files if cache is too large"""
        total_size = sum(info['size'] for info in self.cache_index.values())
        
        if total_size <= self.max_size_bytes:
            return
        
        # Sort by last accessed time (oldest first)
        cache_items = sorted(
            self.cache_index.items(),
            key=lambda x: x[1]['last_accessed']
        )
        
        # Remove oldest items until under limit
        while total_size > self.max_size_bytes and cache_items:
            cache_key, cache_info = cache_items.pop(0)
            
            # Remove file
            if os.path.exists(cache_info['path']):
                os.remove(cache_info['path'])
            
            # Remove from index
            del self.cache_index[cache_key]
            total_size -= cache_info['size']
        
        self.save_cache_index()
    
    def clean_session_cache(self, session_id):
        """Clear cache for specific session"""
        to_remove = []
        for cache_key, cache_info in self.cache_index.items():
            if cache_info['session_id'] == session_id:
                if os.path.exists(cache_info['path']):
                    os.remove(cache_info['path'])
                to_remove.append(cache_key)
        
        for key in to_remove:
            del self.cache_index[key]
        
        self.save_cache_index()
    
    def get_cache_stats(self):
        """Get cache statistics"""
        total_size = sum(info['size'] for info in self.cache_index.values())
        num_files = len(self.cache_index)
        
        return {
            'total_size': total_size,
            'num_files': num_files,
            'max_size': self.max_size_bytes,
            'usage_percent': (total_size / self.max_size_bytes) * 100
        }