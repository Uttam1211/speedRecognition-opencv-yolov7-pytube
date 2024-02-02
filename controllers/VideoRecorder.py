import cv2
import os

class VideoRecorder:
    def __init__(self, output_folder="recorded_videos", fourcc=cv2.VideoWriter_fourcc(*'mp4v')):
        self.output_folder = output_folder
        self.fourcc = fourcc
        self.is_recording = False
        self.video_writer = None
        self.frame_count = 0
        self.video_count = 0

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def start_recording(self, frame_width, frame_height, fps=20.0):
        if not self.is_recording:
            self.video_count += 1
            video_path = os.path.join(self.output_folder, f"video_{self.video_count}.mp4")
            self.video_writer = cv2.VideoWriter(video_path, self.fourcc, fps, (frame_width, frame_height))
            self.is_recording = True

    def record_frame(self, frame):
        if self.is_recording:
            self.video_writer.write(frame)
            self.frame_count += 1

    def stop_recording(self):
        if self.is_recording:
            self.video_writer.release()
            self.is_recording = False
            self.frame_count = 0

    def is_active(self):
        return self.is_recording
