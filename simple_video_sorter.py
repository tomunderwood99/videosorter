import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QUrl, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import time
import video_sorter_keybinding as keybind  # Import keybinding configuration

##################

class VideoPlayer(QWidget):
    def __init__(self, video_folder_path):
        super().__init__()
        self.video_folder_path = video_folder_path
        self.major_seizure_path = self.ensure_folder_exists("Major_Seizure")
        self.minor_seizure_path = self.ensure_folder_exists("Minor_Seizure")
        self.nonseizure_path = self.ensure_folder_exists("Night_Nonseizure")
        self.nonsleeping_path = self.ensure_folder_exists("Day_Nonsleeping")
        self.exclude_path = self.ensure_folder_exists("Exclude")  # New folder/path for excluded videos
        self.current_video_index = 0
        self.video_files = self.get_video_files()
        self.sorted_video_paths = []  # Store paths of sorted videos
        
        # Initialize the video widget and layout before calling initUI
        self.layout = QVBoxLayout()
        self.videoWidget = QVideoWidget()  # Initialize the video widget here
        #self.videoWidget.setMinimumSize(640, 480)  # Set minimum size (width, height)
        
        self.initUI()
        
        self.player = QMediaPlayer(self)  # Use QMediaPlayer for media playback
        self.player.setVideoOutput(self.videoWidget)  # Set the video output to the video widget
        self.isPlaying = False

    def ensure_folder_exists(self, folder_name):
        path = os.path.join(self.video_folder_path, folder_name)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_video_files(self):
        supported_video_formats = ['.mp4', '.avi', '.mov']  # Add or remove video formats as needed
        video_files = [f for f in os.listdir(self.video_folder_path) if os.path.isfile(os.path.join(self.video_folder_path, f)) and os.path.splitext(f)[1].lower() in supported_video_formats]
        return video_files

    def initUI(self):
        self.setWindowTitle("Video Sorter")
        
        # Now self.layout and self.videoWidget are already initialized
        self.layout.addWidget(self.videoWidget)

        # Display video path label
        self.videoPathLabel = QLabel("Video Path: None")
        self.layout.addWidget(self.videoPathLabel)

        # Initialize Play/Pause button with key binding in label
        self.playPauseButton = QPushButton(f"Play ({keybind.play_pause})")
        self.playPauseButton.clicked.connect(self.toggle_play_pause)
        self.layout.addWidget(self.playPauseButton)

        # Add Replay button with key binding in label
        self.replayButton = QPushButton(f"Restart ({keybind.restart})")
        self.replayButton.clicked.connect(self.replay_video)
        self.layout.addWidget(self.replayButton)

        # Add Major Seizure Folder button with key binding in label
        self.majorSeizureButton = QPushButton(f"Major Seizure Folder ({keybind.major_seizure})")
        self.majorSeizureButton.clicked.connect(lambda: self.sort_video("major"))
        self.layout.addWidget(self.majorSeizureButton)

        # Add Minor Seizure Folder button with key binding in label
        self.minorSeizureButton = QPushButton(f"Minor Seizure Folder ({keybind.minor_seizure})")
        self.minorSeizureButton.clicked.connect(lambda: self.sort_video("minor"))
        self.layout.addWidget(self.minorSeizureButton)

        # Modify Non-Seizure Folder button to "Night - Nonseizure" with key binding in label
        self.nonSeizureButton = QPushButton(f"Night - Nonseizure ({keybind.night_nonseizure})")
        self.nonSeizureButton.clicked.connect(lambda: self.sort_video("nonseizure"))
        self.layout.addWidget(self.nonSeizureButton)

        # Add Day - Nonsleeping Folder button with key binding in label
        self.nonsleepingButton = QPushButton(f"Day - Nonsleeping ({keybind.day_nonsleeping})")
        self.nonsleepingButton.clicked.connect(lambda: self.sort_video("nonsleeping"))
        self.layout.addWidget(self.nonsleepingButton)

        # Add Exclude button with key binding in label
        self.excludeButton = QPushButton(f"Exclude ({keybind.exclude})")
        self.excludeButton.clicked.connect(lambda: self.sort_video("exclude"))
        self.layout.addWidget(self.excludeButton)  # New button for excluding videos

        # Add Unsort button with key binding in label
        self.unsortButton = QPushButton(f"Unsort ({keybind.unsort})")
        self.unsortButton.clicked.connect(self.unsort_video)
        self.layout.addWidget(self.unsortButton)

        # Set the layout
        self.setLayout(self.layout)

    def keyPressEvent(self, event):
        if event.key() == getattr(Qt, f"Key_{keybind.major_seizure}"):
            self.sort_video("major")
        elif event.key() == getattr(Qt, f"Key_{keybind.minor_seizure}"):
            self.sort_video("minor")
        elif event.key() == getattr(Qt, f"Key_{keybind.night_nonseizure}"):
            self.sort_video("nonseizure")
        elif event.key() == getattr(Qt, f"Key_{keybind.day_nonsleeping}"):
            self.sort_video("nonsleeping")
        elif event.key() == getattr(Qt, f"Key_{keybind.exclude}"):
            self.sort_video("exclude")
        elif event.key() == getattr(Qt, f"Key_{keybind.play_pause}"):
            self.toggle_play_pause()
        elif event.key() == getattr(Qt, f"Key_{keybind.restart}"):
            self.replay_video()
        elif event.key() == getattr(Qt, f"Key_{keybind.unsort}"):
            self.unsort_video()
        else:
            super().keyPressEvent(event)  # Call the base class method to handle other key presses
    def toggle_play_pause(self):
        if self.isPlaying:
            self.player.pause()
            self.playPauseButton.setText("Play")
        else:
            if self.player.state() == QMediaPlayer.StoppedState and self.current_video_index < len(self.video_files):
                self.load_video()
            else:
                self.player.play()
            self.playPauseButton.setText("Pause")
        self.isPlaying = not self.isPlaying

    def load_video(self):
        video_path = os.path.join(self.video_folder_path, self.video_files[self.current_video_index])
        print(video_path)
        self.videoPathLabel.setText(f"Video Path: {video_path}")  # Update video path label
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        self.player.play()  # Start playback
        self.isPlaying = True

    def sort_video(self, seizure_type):
        if self.current_video_index < len(self.video_files):
            # Ensure the player is stopped and the file is released before moving it
            self.player.stop()
            QApplication.processEvents()  # Process any pending events to ensure the file is released

            source = os.path.join(self.video_folder_path, self.video_files[self.current_video_index])
            if seizure_type == "major":
                destination = self.major_seizure_path
            elif seizure_type == "minor":
                destination = self.minor_seizure_path
            elif seizure_type == "nonsleeping": 
                destination = self.nonsleeping_path
            elif seizure_type == "exclude":  # Condition for excluding videos
                destination = self.exclude_path
            else:
                destination = self.nonseizure_path
            
            try:
                shutil.move(source, destination)
                self.sorted_video_paths.append((source, destination))  # Store the source and destination paths
                
                # Remove the sorted video from the list and adjust the index accordingly
                del self.video_files[self.current_video_index]
                
                if self.current_video_index < len(self.video_files):
                    # Wait a bit before loading the next video to ensure the file system has updated
                    QTimer.singleShot(100, self.load_video)
                else:
                    QMessageBox.information(self, "Done", "No more videos to sort.")
                    self.close()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to move file: {e}")

    def unsort_video(self):
        if self.sorted_video_paths:
            source, destination = self.sorted_video_paths.pop()  # Get the last sorted video's paths
            video_file_name = os.path.basename(source)  # Extract the video file name
            original_source = os.path.join(self.video_folder_path, video_file_name)  # Construct the original source path
            
            # Ensure destination points to the specific file, not just the folder
            destination_file_path = os.path.join(destination, video_file_name)
            
            shutil.move(destination_file_path, original_source)  # Move it back to the original folder
            self.video_files.insert(self.current_video_index, video_file_name)  # Reinsert the video file name into the list
            self.current_video_index = max(0, self.current_video_index - 1)  # Update the video index
            time.sleep(0.1)  # Pause for 0.1 second
            self.load_video()  # Replay the unsorted video
        else:
            QMessageBox.warning(self, "Error", "No videos to unsort.")

    def replay_video(self):
        self.player.setPosition(0)  # Seek to the beginning
        if not self.isPlaying:
            self.player.play()
            self.isPlaying = True
    # Methods toggle_play_pause, load_video, sort_video, unsort_video, and replay_video remain unchanged

def ask_paths():
    app = QApplication(sys.argv)
    video_folder_path = QFileDialog.getExistingDirectory(None, "Select Unsorted Video Folder")
    if video_folder_path:
        return video_folder_path
    else:
        QMessageBox.warning(None, "Error", "Please select the path for unsorted videos.")
        sys.exit()

if __name__ == "__main__":
    video_folder_path = ask_paths()
    if video_folder_path:
        app = QApplication(sys.argv)
        ex = VideoPlayer(video_folder_path)
        ex.show()
        sys.exit(app.exec_())
    else:
        QMessageBox.warning(None, "Error", "Please select the path for unsorted videos.")

