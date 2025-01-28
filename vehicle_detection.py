import cv2
import numpy as np
import easyocr
from typing import Tuple, Dict, List

class VehicleDetector:
    def __init__(self):
        self.plate_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml'
        )
        self.reader = easyocr.Reader(['en'])
        self.prev_positions = {}  # Store previous positions for speed calculation
        self.color_ranges = {
            'red': ([0, 50, 50], [10, 255, 255]),
            'blue': ([110, 50, 50], [130, 255, 255]),
            'green': ([50, 50, 50], [70, 255, 255]),
            'white': ([0, 0, 200], [180, 30, 255]),
            'black': ([0, 0, 0], [180, 255, 30])
        }

    def detect_plate(self, frame) -> Tuple[np.ndarray, List[str]]:
        """Detect and recognize license plates in the frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = self.plate_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(25, 25)
        )

        plate_texts = []
        for (x, y, w, h) in plates:
            # Draw rectangle around plate
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Extract plate region
            plate_region = gray[y:y+h, x:x+w]

            # OCR on plate region
            results = self.reader.readtext(plate_region)
            if results:
                text = results[0][1]
                plate_texts.append(text)
                cv2.putText(
                    frame,
                    text,
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2
                )

        return frame, plate_texts

    def detect_color(self, frame, bbox) -> str:
        """Detect dominant color of vehicle"""
        x, y, w, h = bbox
        vehicle_region = frame[y:y+h, x:x+w]
        hsv = cv2.cvtColor(vehicle_region, cv2.COLOR_BGR2HSV)

        max_pixels = 0
        detected_color = "unknown"

        for color, (lower, upper) in self.color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            pixels = cv2.countNonZero(mask)
            if pixels > max_pixels:
                max_pixels = pixels
                detected_color = color

        return detected_color

    def estimate_speed(self, vehicle_id: str, bbox: Tuple[int, int, int, int], 
                      fps: float = 30.0) -> float:
        """Estimate vehicle speed based on position change"""
        x, y, w, h = bbox
        center = (x + w//2, y + h//2)

        if vehicle_id not in self.prev_positions:
            self.prev_positions[vehicle_id] = {
                'position': center,
                'time': cv2.getTickCount()
            }
            return 0.0

        # Calculate pixel distance moved
        prev = self.prev_positions[vehicle_id]['position']
        prev_time = self.prev_positions[vehicle_id]['time']
        current_time = cv2.getTickCount()

        # Time difference in seconds
        time_diff = (current_time - prev_time) / cv2.getTickFrequency()

        # Calculate distance moved in pixels
        pixel_distance = np.sqrt(
            (center[0] - prev[0])**2 + (center[1] - prev[1])**2
        )

        # Convert pixel distance to meters (approximate)
        meters_per_pixel = 0.1  # This should be calibrated based on camera setup
        distance = pixel_distance * meters_per_pixel

        # Calculate speed (m/s to km/h)
        speed = (distance / time_diff) * 3.6

        # Update previous position
        self.prev_positions[vehicle_id] = {
            'position': center,
            'time': current_time
        }

        return speed

    def determine_direction(self, vehicle_id: str, current_pos: Tuple[int, int]) -> str:
        """Determine vehicle movement direction"""
        if vehicle_id not in self.prev_positions:
            return "unknown"

        prev_pos = self.prev_positions[vehicle_id]['position']
        dx = current_pos[0] - prev_pos[0]
        dy = current_pos[1] - prev_pos[1]

        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"

    def analyze_vehicle(self, frame, bbox) -> Dict:
        """Comprehensive vehicle analysis"""
        x, y, w, h = bbox
        vehicle_id = f"vehicle_{x}_{y}"

        # Get center position
        center = (x + w//2, y + h//2)

        # Analyze vehicle
        color = self.detect_color(frame, (x, y, w, h))
        speed = self.estimate_speed(vehicle_id, (x, y, w, h))
        direction = self.determine_direction(vehicle_id, center)

        return {
            'id': vehicle_id,
            'bbox': (x, y, w, h),
            'color': color,
            'speed': speed,
            'direction': direction,
            'position': center
        }