import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk
import cv2
import threading
from controllers.VideoProcessor import VideoProcessor
from pytube import YouTube
from tkinter import ttk  # Import ttk from tkinter
from controllers.MediaCompressor import MediaCompressor

class SpeedCameraApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.video_processor = VideoProcessor(frame_rate=15)
        self.media_compressor = MediaCompressor(self.window)

        # Set fixed size for the window
        self.window.geometry('800x600')  # size, adjust as needed
        self.window.resizable(False, False)  # Disable resizing

        # Initialize Video Capture
        self.cap = None
        self.video_label = None  # Use a Label for video display
        self.is_running = False
        self.no_video_text = "No video"
        self.capture_counter = 0

        # Create a frame for buttons
        self.button_frame = ttk.Frame(self.window)  # Use ttk.Frame
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        # Button to stop the video
        self.btn_stop_video = ttk.Button(self.button_frame, text="Stop Video", style='Red.TButton', command=self.stop_video, state=tk.DISABLED)
        self.btn_stop_video.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Buttons for control
        self.btn_load_video = ttk.Button(self.button_frame, text="Load Img / Video", command=self.open_video)
        self.btn_load_video.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_capture_image = ttk.Button(self.button_frame, text="Capture Image", command=self.capture_image, state=tk.DISABLED)
        self.btn_capture_image.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_connect_live = ttk.Button(self.button_frame, text="Connect to Live Video", command=self.connect_live)
        self.btn_connect_live.pack(side=tk.LEFT, padx=10, pady=10)

        self.feature_options = ["Select Feature", "Compress", "Correct Distortion", "Stitch"]
        self.selected_feature = tk.StringVar()
        self.feature_combobox = ttk.Combobox(self.button_frame, textvariable=self.selected_feature, values=self.feature_options, state="readonly")
        self.feature_combobox.current(0)
        self.feature_combobox.pack(side=tk.RIGHT, padx=10, pady=10)
        self.feature_combobox.bind("<<ComboboxSelected>>", self.handle_feature_selection)

        # Video display area
        self.video_area = tk.Canvas(self.window, width=800, height=480, bg='black')
        self.video_area.pack(pady=10)
        self.video_area.create_text(390, 240, text=self.no_video_text, fill="white", font=('Helvetica', 16))

    def open_video(self):
        self.video_source = filedialog.askopenfilename()  # Choose file
        if not self.video_source:
            return

        self.cap = cv2.VideoCapture(self.video_source)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Unable to open video file.")
            return

        self.start_video_stream()

    def start_video_stream(self):
        if self.video_label is not None:
            self.video_label.destroy()

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate scaling factors to fit the video within the fixed display area
        scale_width = 800 / width
        scale_height = 480 / height
        scale_factor = min(scale_width, scale_height)

        # Calculate the new width and height for the video
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Read the first frame
        ret, frame = self.cap.read()
        if ret:
            frame = self.video_processor.detect_objects(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resized_frame = cv2.resize(frame, (new_width, new_height))

            photo = ImageTk.PhotoImage(image=Image.fromarray(resized_frame))
            self.video_label = tk.Label(self.video_area, image=photo, bg='black')
            self.video_label.image = photo  # Keep a reference to the image to prevent garbage collection
            self.video_label.pack(fill=tk.BOTH, expand=True)

        self.is_running = True
        self.btn_capture_image['state'] = tk.NORMAL
        self.btn_stop_video['state'] = tk.NORMAL
        threading.Thread(target=self.video_stream, daemon=True).start()

    def video_stream(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                frame = self.video_processor.detect_objects(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                resized_frame = cv2.resize(frame, (self.video_label.winfo_width(), self.video_label.winfo_height()))

                photo = ImageTk.PhotoImage(image=Image.fromarray(resized_frame))
                self.video_label.config(image=photo)  # Update the video_label image
                self.video_label.image = photo  # Keep a reference to the image to prevent garbage collection
            else:
                break

    def capture_image(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                capture_folder = "captured"
                os.makedirs(capture_folder, exist_ok=True)
                filename = f"{capture_folder}/captured_frame_{self.capture_counter}.jpg"
                cv2.imwrite(filename, frame)
                messagebox.showinfo("Info", f"Image captured successfully as {filename}.")
                self.capture_counter += 1
            else:
                messagebox.showerror("Error", "Failed to capture image.")

    def connect_live(self):
        # Prompt for YouTube URL
        youtube_url = simpledialog.askstring("Input", "Enter YouTube Video URL:",
                                            parent=self.window)

        if youtube_url:
            try:
                yt = YouTube(youtube_url)
                video_stream = yt.streams.filter(file_extension='mp4').first()
                if video_stream:
                    # Get the stream URL
                    stream_url = video_stream.url
                    # Open the video stream
                    self.cap = cv2.VideoCapture(stream_url)
                    if not self.cap.isOpened():
                        messagebox.showerror("Error", "Failed to open video stream.")
                        return
                    
                    # Proceed to start the video stream processing
                    self.start_video_stream()
                else:
                    messagebox.showerror("Error", "No suitable video stream found.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch video stream. Error: {e}")
    def stop_video(self):
            if self.cap and self.cap.isOpened():
                self.cap.release()  # Release the video capture
            #self.video_processor = None
            self.is_running = False
            self.btn_capture_image['state'] = tk.DISABLED
            self.video_area.delete("all")  # Clear the video display area
            self.video_area.create_text(390, 240, text=self.no_video_text, fill="white", font=('Helvetica', 16))

    def handle_feature_selection(self, event):
        selected = self.selected_feature.get()
        if selected == "Compress":
            self.compress_media()
        elif selected == "Correct Distortion":
            self.correct_distortion()
        elif selected == "Stitch":
            self.stitch_media()
        self.feature_combobox.current(0)  # Reset the combobox selection

    def compress_media(self):
        self.media_compressor.compress_media()
        

    def correct_distortion(self):
        messagebox.showinfo("Info", " Distoration Feature Not Implemented Yet.")

    def stitch_media(self):
        # Dummy implementation for demonstration
        messagebox.showinfo("Info", "Stitch Feature Not Implemented Yet.")

    def __del__(self):
        self.is_running = False
        if self.cap:
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedCameraApp(root, "Speed Camera Application")
    root.mainloop()
