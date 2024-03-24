# Simple Video Sorter

This is a simple GUI application designed for sorting videos, compatible with both Mac and Windows platforms. It offers a user-friendly interface to categorize your video files efficiently, making it an ideal tool for organizing videos for machine learning projects or personal use.

## Features

- **Customizable Keybindings:** Set your preferred shortcuts for play/pause, restart, unsort, and sorting into specific folders.
- **Folder Sorting:** Easily configure the application to sort videos into designated folders based on your keybindings.
- **Save Settings:** Your keybindings, folder mappings, and video directory path can be saved for future sessions, streamlining your workflow.

## Running the Application

### As an Executable

1. **Download the Executable:** Download the executable file suitable for your operating system and the keybinding file. **Ensure that the executable and the `video_sorter_keybinding.py` file are in the same directory.**
2. **Run the Application:** Launch the executable. Upon first run, you'll be prompted to input your desired keybindings, folders for sorting, and the path to the unsorted videos. These settings can be saved to the `video_sorter_keybinding.py` file for convenience in future uses.

### As a Script

If you prefer to run the application as a script, follow these steps:

1. **Create a Conda Environment:** Set up a new Conda environment using Python 3.12.0:
    conda create --name your_env_name python=3.12.0
2. **Install PyQt5:** Use pip to install the PyQt5 package required for the GUI:
    pip install PyQt5
3. **Run the Script:** Navigate to the directory containing `simple_video_sorter.py` and execute the script:
    python simple_video_sorter.py


## Dependencies

- **Python 3.12.0:** Ensure you have Python version 3.12.0 installed in your environment.
- **PyQt5:** This package is used for the GUI components of the application.
- **GStreamer (Mac/Linux) or K-Lite Codec Pack (Windows):** These are required for video playback functionality.

## Purpose

Originally developed to assist in sorting videos for machine learning datasets, this application is designed to be flexible and robust enough for various use cases. Whether you're organizing personal video collections or preparing data for analysis, Simple Video Sorter can help streamline the process.
