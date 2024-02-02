import math

class SpeedCalculator:
    def __init__(self, frame_rate, pixel_to_meter_ratio=0.05):
        # Frame rate in frames per second
        self.frame_rate = frame_rate
        # Assumed conversion ratio from pixels to meters
        self.pixel_to_meter_ratio = pixel_to_meter_ratio

    def calculate_speed(self, x1, y1, timestamp1, x2, y2, timestamp2):
        # Calculate time elapsed between frames in seconds
        time_seconds = timestamp2 - timestamp1

        if time_seconds <= 0:
            return None  # Invalid time difference

        # Simplified distance calculation (straight-line distance in pixels)
        distance_pixels = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # Convert distance from pixels to meters
        distance_meters = distance_pixels * self.pixel_to_meter_ratio

        # Calculate speed in meters per second
        speed_meters_per_sec = distance_meters / time_seconds

        # Convert speed to miles per hour (1 m/s is approximately 2.23694 mph)
        speed_mph = speed_meters_per_sec * 2.23694

        return speed_mph
