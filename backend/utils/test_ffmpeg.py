import subprocess
import os

# Test if ffmpeg works
result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
print("FFmpeg test:", "SUCCESS" if result.returncode == 0 else "FAILED")
print("Output:", result.stdout[:200])

# Test if our directories exist
print("\nChecking directories:")
print("Uploads folder exists:", os.path.exists('static/uploads'))
print("Cache folder exists:", os.path.exists('static/cache'))
print("Templates folder exists:", os.path.exists('templates'))