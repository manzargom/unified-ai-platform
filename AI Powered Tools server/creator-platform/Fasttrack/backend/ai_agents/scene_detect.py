import cv2
import numpy as np

class SceneDetector:
    def __init__(self):
        self.threshold = 30.0
    
    def detect(self, video_path):
        """Detect scene changes"""
        scenes = []
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            prev_frame = None
            scene_start = 0
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    diff = cv2.absdiff(gray, prev_frame)
                    mean_diff = np.mean(diff)
                    
                    if mean_diff > self.threshold:
                        scene_end = frame_count / fps
                        scenes.append({
                            'start': scene_start,
                            'end': scene_end,
                            'type': 'cut'
                        })
                        scene_start = scene_end
                
                prev_frame = gray
                frame_count += 1
            
            cap.release()
            return scenes
        except Exception as e:
            print(f"Error: {e}")
            return []