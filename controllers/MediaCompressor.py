import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import os
import numpy as np

class MediaCompressor:
    def __init__(self, parent_window):
        self.parent_window = parent_window

    def compress_media(self):
        media_path = filedialog.askopenfilename(title="Select Image/Video", filetypes=[("Media Files", "*.jpeg *.jpg *.png *.mp4 *.avi")])
        if not media_path:
            return

        media_type = "image" if media_path.lower().endswith(('.png', '.jpg', '.jpeg')) else "video"
        
        popup = tk.Toplevel(self.parent_window)
        popup.title("Compress Media")
        popup.geometry("300x200")
        popup.focus_force()  # Force focus on the pop-up

        if media_type == "image":
            img = Image.open(media_path)
            img.thumbnail((100, 100), Image.Resampling.LANCZOS)  # Use Resampling.LANCZOS
            self.photo = ImageTk.PhotoImage(img)  # Keep reference at the instance level
            label = tk.Label(popup, image=self.photo)
            label.pack(pady=10)

        progress = ttk.Progressbar(popup, orient=tk.HORIZONTAL, length=200, mode='determinate')
        progress.pack(pady=10)

        start_btn = ttk.Button(popup, text="Start Compression", command=lambda: self.start_compression(media_path, progress, media_type))
        start_btn.pack(pady=10)

        self.parent_window.update_idletasks()  # Update the parent window
    
    def start_compression(self, media_path, progress_bar, media_type):
        output_folder = os.path.join(os.path.dirname(media_path), "CompressedMedia")
        os.makedirs(output_folder, exist_ok=True)

        output_path = os.path.join(output_folder, os.path.basename(media_path))
        
        if media_type == "image":
            self.compress_image(media_path, output_path, progress_bar)
        else:
            self.compress_video(media_path, output_path, progress_bar)

        messagebox.showinfo("Compression Complete", f"Media compressed and saved to {output_path}")

    def compress_image(self, input_path, output_path, progress_bar):
        with Image.open(input_path) as img:
            progress_bar['value'] = 50
            self.parent_window.update_idletasks()
            img.save(output_path, "JPEG", quality=20)
            progress_bar['value'] = 100

    def compress_video(self, input_path, output_path, progress_bar):
        cap = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        for i in range(frame_count):
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                out.write(frame)
                progress_bar['value'] = (i + 1) / frame_count * 100
                self.parent_window.update_idletasks()
            else:
                break
        
        cap.release()
        out.release()
        progress_bar['value'] = 100
