import cv2
import numpy as np
import time

from controllers.SpeedCalculator import SpeedCalculator
from controllers.VideoRecorder import VideoRecorder


class VideoProcessor:
    def __init__(self,frame_rate=15):
        # Initialize variables for tracking
        self.prev_objects = {}
        # Initialize SpeedCalculator with appropriate parameters
        self.speed_calculator = SpeedCalculator(frame_rate)
        self.video_recorder = VideoRecorder()
        # Load YOLOv7
        self.net = cv2.dnn.readNet("Models/yolov7.weights", "Models/yolov7.cfg")
        layer_names = self.net.getLayerNames()

        out_layers = self.net.getUnconnectedOutLayers()
        if out_layers.ndim == 1:
            self.output_layers = [layer_names[i - 1] for i in out_layers]
        else:
            self.output_layers = [layer_names[i[0] - 1] for i in out_layers]

        # Load class names
        with open("coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

    def detect_objects(self, frame):
        height, width, channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        class_ids = []
        confidences = []
        boxes = []

        current_timestamp = time.time()

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        detected_objects = len(indexes) > 0

       # Use video_recorder's is_active() method to check recording status
        if detected_objects and not self.video_recorder.is_active():
            self.video_recorder.start_recording(width, height)
        elif not detected_objects and self.video_recorder.is_active():
            self.video_recorder.stop_recording()


        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                confidence = confidences[i]
                color = np.random.uniform(0, 255, size=(3,))

                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, f"{label}: {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                object_id = label + str(i)  # Unique ID for each object
                speed_mph = 0  # Default speed
                if object_id in self.prev_objects:
                    prev_x, prev_y, prev_timestamp = self.prev_objects[object_id]
                    speed_mph = self.speed_calculator.calculate_speed(prev_x, prev_y, prev_timestamp, x, y, current_timestamp)
                    speed_mph = int(speed_mph) if speed_mph is not None else 0

                # Display speed on the frame
                cv2.putText(frame, f"Speed: {speed_mph:.2f} mph", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                self.prev_objects[object_id] = (x, y, current_timestamp)

        if self.video_recorder.is_active():
            self.video_recorder.record_frame(frame)

        return frame

    
    def __del__(self):
        # Ensure resources are released properly
        if self.is_recording:
            self.video_recorder.stop_recording()