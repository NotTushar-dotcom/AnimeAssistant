import os
from PySide6.QtGui import QMovie

class AnimationManager:
    def __init__(self, label):
        self.label = label
        self.animations_path = os.path.join(os.path.dirname(__file__), "../assets/videos")
        self.current_movie = None

    def set_animation(self, emotion):
        gif_path = os.path.join(self.animations_path, f"{emotion}.mp4.gif")

        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            self.label.setMovie(movie)
            movie.start()
            self.current_movie = movie
        else:
            print(f"[WARNING] Animation for '{emotion}' not found at {gif_path}")
