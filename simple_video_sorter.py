# May need to install GStreamer on Mac/Linux 
# or K-Lite Codec Pack on Windows

# To run as script:
# 1) create conda env using python 3.12.0 
#    conda create --name your_env_name python=3.12.0
# 2) install PyQt5 with pip
#    pip install PyQt5

import sys
import os
import shutil
import ast
import importlib.util
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QMessageBox, QLineEdit, QFormLayout, QDialog, QDialogButtonBox, QCheckBox, QSizePolicy)
from PyQt5.QtCore import QTimer, QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

# Function to dynamically load the configuration
def load_config():
    # First, try to load the configuration from the executable's directory
    exe_dir = os.path.dirname(sys.executable)
    config_path_exe = os.path.join(exe_dir, 'video_sorter_keybinding.py')
    
    # Then, define the path in the current working directory
    cwd = os.getcwd()
    config_path_cwd = os.path.join(cwd, 'video_sorter_keybinding.py')
    
    # Check if the config exists in the executable's directory
    if os.path.exists(config_path_exe):
        config_path = config_path_exe
    elif os.path.exists(config_path_cwd):
        # If not, fall back to the current working directory
        config_path = config_path_cwd
    else:
        raise FileNotFoundError("video_sorter_keybinding.py not found in either the executable's directory or the current working directory.")
    
    spec = importlib.util.spec_from_file_location("video_sorter_keybinding", config_path)
    video_sorter_keybinding = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(video_sorter_keybinding)
    return video_sorter_keybinding

class KeybindingConfigurator(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configure Keybindings, Folders, and Video Path")
        self.layout = QVBoxLayout()
        
        self.formLayout = QFormLayout()
        self.core_buttons = {
            'play_pause': QLineEdit('Space'),
            'restart': QLineEdit('R'),
            'unsort': QLineEdit('U')
        }
        
        for action, lineEdit in self.core_buttons.items():
            self.formLayout.addRow(f"{action.replace('_', ' ').title()}: ", lineEdit)
        
        self.videoFolderPathLineEdit = QLineEdit()
        self.formLayout.addRow("Path to Unsorted Videos Folder: ", self.videoFolderPathLineEdit)
        
        self.folderMappingsLayout = QVBoxLayout()
        self.folderMappings = []
        self.addFolderMappingButton = QPushButton("Add Sorting Category and Keybinding")
        self.addFolderMappingButton.clicked.connect(self.addFolderMapping)
        
        self.layout.addLayout(self.formLayout)
        self.layout.addLayout(self.folderMappingsLayout)
        self.layout.addWidget(self.addFolderMappingButton)
        
        self.useDefaultCheckbox = QCheckBox("Load keybindings (and video path unless provided)")
        self.layout.addWidget(self.useDefaultCheckbox)
        
        self.saveSettingsCheckbox = QCheckBox("Save these keybindings as default")
        self.layout.addWidget(self.saveSettingsCheckbox)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.onAccept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        
        self.setLayout(self.layout)
    
    def addFolderMapping(self):
        folderLineEdit = QLineEdit()
        keyLineEdit = QLineEdit()
        mappingLayout = QFormLayout()
        mappingLayout.addRow("Folder Name: ", folderLineEdit)
        mappingLayout.addRow("Key: ", keyLineEdit)
        self.folderMappingsLayout.addLayout(mappingLayout)
        self.folderMappings.append((folderLineEdit, keyLineEdit))
    
    def getConfig(self):
        if self.useDefaultCheckbox.isChecked():
            video_sorter_keybinding = load_config()
            core_buttons = video_sorter_keybinding.core_buttons
            folders_to_sort = video_sorter_keybinding.folders_to_sort
            video_folder_path = self.videoFolderPathLineEdit.text() if self.videoFolderPathLineEdit.text() else video_sorter_keybinding.unsorted_path
        else:
            core_buttons = {action: le.text() for action, le in self.core_buttons.items()}
            folders_to_sort = {folder.text(): key.text() for folder, key in self.folderMappings}
            video_folder_path = self.videoFolderPathLineEdit.text()
        return video_folder_path, core_buttons, folders_to_sort

    def onAccept(self):
        video_folder_path, core_buttons, folders_to_sort = self.getConfig()
        if self.useDefaultCheckbox.isChecked() and self.videoFolderPathLineEdit.text():
            self.saveConfig(video_folder_path, core_buttons, folders_to_sort)
        elif self.saveSettingsCheckbox.isChecked():
            self.saveConfig(video_folder_path, core_buttons, folders_to_sort)
        self.accept()

    def saveConfig(self, video_folder_path, core_buttons, folders_to_sort):
        settings_content = f"""
\"\"\"
This file is auto-generated by the KeybindingConfigurator.
\"\"\"

unsorted_path = "{video_folder_path}"

core_buttons = {ast.literal_eval(repr(core_buttons))}

folders_to_sort = {ast.literal_eval(repr(folders_to_sort))}
"""
        exe_dir = os.path.dirname(sys.executable)
        config_path = os.path.join(exe_dir, 'video_sorter_keybinding.py')
        with open(config_path, 'w') as file:
            file.write(settings_content)

class VideoPlayer(QWidget):
    def __init__(self, video_folder_path, core_buttons, folders_to_sort):
        super().__init__()
        self.video_folder_path = video_folder_path
        self.core_buttons = core_buttons
        self.folders_to_sort = folders_to_sort
        self.folder_paths = {}
        self.current_video_index = 0
        self.video_files = self.get_video_files()
        self.sorted_video_paths = []
        
        # Check if the video_files list is empty and show a warning if it is
        if not self.video_files:
            QMessageBox.warning(self, "No Videos Found", "No video files found in the provided path.")
            sys.exit()  # Exit the application if no video files are found
        
        self.layout = QVBoxLayout()
        self.videoWidget = QVideoWidget()
        
        self.initUI()
        
        self.player = QMediaPlayer(self)
        self.player.setVideoOutput(self.videoWidget)
        self.isPlaying = False

    def ensure_folder_exists(self, folder_name):
        path = os.path.join(self.video_folder_path, folder_name)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_video_files(self):
        supported_video_formats = ['.mp4', '.avi', '.mov']
        video_files = [f for f in os.listdir(self.video_folder_path) if os.path.isfile(os.path.join(self.video_folder_path, f)) and os.path.splitext(f)[1].lower() in supported_video_formats]
        return video_files

    def initUI(self):
        self.setWindowTitle("Video Sorter")
        self.layout.addWidget(self.videoWidget)
        self.videoPathLabel = QLabel("Click play to start sorting")
        
        # Adjust the size policy of the videoPathLabel to reduce vertical space
        sizePolicy = self.videoPathLabel.sizePolicy()
        sizePolicy.setVerticalPolicy(QSizePolicy.Maximum)
        self.videoPathLabel.setSizePolicy(sizePolicy)
        
        self.layout.addWidget(self.videoPathLabel)

        self.playPauseButton = QPushButton(f"Play/Pause ({self.core_buttons['play_pause']})")
        self.playPauseButton.clicked.connect(self.toggle_play_pause)
        self.layout.addWidget(self.playPauseButton)

        self.restartButton = QPushButton(f"Restart ({self.core_buttons['restart']})")
        self.restartButton.clicked.connect(self.replay_video)
        self.layout.addWidget(self.restartButton)

        self.unsortButton = QPushButton(f"Unsort ({self.core_buttons['unsort']})")
        self.unsortButton.clicked.connect(self.unsort_video)
        self.layout.addWidget(self.unsortButton)

        for folder_name, key in self.folders_to_sort.items():
            folder_path = self.ensure_folder_exists(folder_name.replace("_", " ").title())
            self.folder_paths[folder_name] = folder_path
            button = QPushButton(f"{folder_name.replace('_', ' ').title()} ({key})")
            button.clicked.connect(lambda checked, fn=folder_name: self.sort_video(fn))
            self.layout.addWidget(button)

        self.setLayout(self.layout)

    def keyPressEvent(self, event):
        key_mappings = {**self.core_buttons, **self.folders_to_sort}
        reverse_mappings = {v: k for k, v in key_mappings.items()}
        
        # Handle space key separately
        if event.key() == Qt.Key_Space:
            self.toggle_play_pause()
            return

        key_pressed = event.text().upper()

        if key_pressed in reverse_mappings:
            action = reverse_mappings[key_pressed]
            if action in self.core_buttons:
                if action == "play_pause":
                    self.toggle_play_pause()
                elif action == "restart":
                    self.replay_video()
                elif action == "unsort":
                    self.unsort_video()
            elif action in self.folders_to_sort:
                self.sort_video(action)
        else:
            super().keyPressEvent(event)

    def toggle_play_pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.playPauseButton.setText("Play")
            self.isPlaying = False  # Explicitly set to False when paused
        else:
            if self.player.state() == QMediaPlayer.StoppedState and self.current_video_index < len(self.video_files):
                self.load_video()
            else:
                self.player.play()
                self.playPauseButton.setText("Pause")
            self.isPlaying = True  # Explicitly set to True when playing

    def load_video(self):
        video_path = os.path.join(self.video_folder_path, self.video_files[self.current_video_index])
        self.videoPathLabel.setText(f"Video Path: {video_path}")  # Update video path label
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        self.player.play()  # Start playback
        self.isPlaying = True  # Ensure isPlaying reflects the current state

    def sort_video(self, folder_name):
        if self.current_video_index < len(self.video_files) and (self.isPlaying or self.player.state() == QMediaPlayer.PausedState):
            self.player.stop()
            self.isPlaying = False  # Update isPlaying since the video will stop
            source = os.path.join(self.video_folder_path, self.video_files[self.current_video_index])
            destination = self.folder_paths[folder_name]
            
            try: 
                # Attempt to move the file
                shutil.move(source, destination)
                self.sorted_video_paths.append((source, destination))
                
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
        else:
            QMessageBox.warning(self, "Error", "You must play the video before sorting it!")

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
            self.load_video()  # Replay the unsorted video
            self.isPlaying = True  # Assume video is playing after unsorting
        else:
            QMessageBox.warning(self, "Error", "No videos to unsort.")

    def replay_video(self):
        self.player.setPosition(0)  # Seek to the beginning
        if not self.isPlaying:
            self.player.play()
            self.isPlaying = True

def ask_paths():
    app = QApplication(sys.argv)
    
    keybindingConfigurator = KeybindingConfigurator()
    if keybindingConfigurator.exec_() == QDialog.Accepted:
        video_folder_path, core_buttons, folders_to_sort = keybindingConfigurator.getConfig()
        if not video_folder_path:
            QMessageBox.warning(None, "Error", "Please enter the path for unsorted videos.")
            sys.exit()
        return video_folder_path, core_buttons, folders_to_sort
    else:
        QMessageBox.warning(None, "Error", "Keybindings and folder mappings configuration cancelled.")
        sys.exit()

if __name__ == "__main__":
    video_folder_path, core_buttons, folders_to_sort = ask_paths()
    if video_folder_path:
        app = QApplication(sys.argv)
        ex = VideoPlayer(video_folder_path, core_buttons, folders_to_sort)
        ex.show()
        ret = app.exec_()
        sys.exit(ret)
    else:
        QMessageBox.warning(None, "Error", "Please select the path for unsorted videos.")