import sys
import os
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QMovie

class AnimeAssistant(QWidget):
    def __init__(self, gif_path):
        super().__init__()

        # Window setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Load animation
        if not os.path.exists(gif_path):
            raise FileNotFoundError(f"GIF not found: {gif_path}")

        self.label = QLabel(self)
        self.movie = QMovie(gif_path)
        self.label.setMovie(self.movie)
        self.movie.start()

        self.resize(300, 300)  # Window size
        self.move_to_bottom_right()

        # Dragging variables
        self.dragging = False
        self.offset = QPoint()

    def move_to_bottom_right(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = screen_geometry.width() - self.width() - 20
        y = screen_geometry.height() - self.height() - 50
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToGlobal(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        self.dragging = False

def run_ui():
    app = QApplication(sys.argv)
    window = AnimeAssistant("assets/videos/idle.mp4.gif")  # Path to your idle gif
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()
