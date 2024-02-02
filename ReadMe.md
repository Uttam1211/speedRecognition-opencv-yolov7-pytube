- Download yolov7 weight and place it in Models before running code locally
  ```sh https://sourceforge.net/projects/darknet-yolo.mirror/files/yolov4/yolov7.weights/download ```
# Speed Camera Application

## Description

The Speed Camera Application is designed to monitor and analyze the speeds of various moving objects to enhance pedestrian safety. This Python-based application utilizes OpenCV for computer vision tasks and Tkinter for the graphical user interface.

## Setup and Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- Access to a command-line interface (CLI) such as Terminal on macOS, Command Prompt or PowerShell on Windows, or a terminal emulator for Linux.

### Creating a Virtual Environment

Before running the application, it's recommended to create a virtual environment. This ensures that the application dependencies are isolated from other Python projects. Here's how to create one:

#### For macOS and Linux:

```sh
python3 -m venv speedcam-env
source speedcam-env/bin/activate
```

#### For Windows:

```sh
python -m venv speedcam-env
speedcam-env\Scripts\activate.bat
```

#### Install Packages

```sh
pip install -r requirements.txt

pip install numpy opencv-python-headless pillow pytube

```

#### Run App

```sh
python SpeedCameraApp.py
```
