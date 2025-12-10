# backend/ai_agents/captions.py
class CaptionAgent:
    def __init__(self):
        self.model = WhisperModel()
    
    async def transcribe(self, video_path):
        # Extract audio
        # Transcribe with Whisper
        # Return timed captions
        pass
    
    async def auto_sync(self, captions, video):
        # Auto-sync captions to speaking
        # Add animations
        pass