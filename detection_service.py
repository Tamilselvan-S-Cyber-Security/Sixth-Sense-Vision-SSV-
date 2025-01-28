import os
import cv2
import numpy as np
from PIL import Image
import io
import base64
from datetime import datetime
import requests

class DetectionService:
    def __init__(self):
        try:
            # Initialize cascade classifiers
            self.car_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_car.xml'
            )
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )

            # Motion detection parameters
            self.prev_frame = None
            self.motion_threshold = 25
            self.min_motion_area = 500

            # Detection history
            self.detection_history = []
            self.max_history = 1000

            self.initialized = True

        except Exception as e:
            print(f"Error initializing detection service: {str(e)}")
            self.initialized = False

    def set_sensitivity(self, sensitivity: int):
        """Adjust motion detection sensitivity (0-100)"""
        self.motion_threshold = int(50 - (sensitivity * 0.4))
        self.min_motion_area = int(1000 - (sensitivity * 8))

    def detect_motion(self, frame):
        """Enhanced motion detection with zone analysis"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if self.prev_frame is None:
                self.prev_frame = gray
                return False, frame, []

            frame_delta = cv2.absdiff(self.prev_frame, gray)
            thresh = cv2.threshold(frame_delta, self.motion_threshold, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)

            contours, _ = cv2.findContours(
                thresh.copy(),
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            motion_detected = False
            motion_zones = []

            for contour in contours:
                if cv2.contourArea(contour) < self.min_motion_area:
                    continue

                motion_detected = True
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Calculate motion zone
                center_x = x + w//2
                center_y = y + h//2
                frame_h, frame_w = frame.shape[:2]

                # Determine zone (divide frame into 9 zones)
                zone_x = center_x // (frame_w // 3)
                zone_y = center_y // (frame_h // 3)
                zone_id = zone_y * 3 + zone_x
                motion_zones.append(zone_id)

            self.prev_frame = gray
            return motion_detected, frame, motion_zones
        except Exception as e:
            print(f"Error in motion detection: {str(e)}")
            return False, frame, []

    def process_image(self, image):
        """Process image for detection"""
        try:
            if not self.initialized:
                return [], image

            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            detections = []

            # Motion detection
            motion_detected, img, motion_zones = self.detect_motion(img)
            if motion_detected:
                detections.append({
                    'class': 'motion',
                    'confidence': 1.0,
                    'zones': motion_zones,
                    'timestamp': datetime.now().isoformat()
                })

            # Vehicle detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            vehicles = self.car_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            for (x, y, w, h) in vehicles:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                detections.append({
                    'class': 'vehicle',
                    'confidence': 0.85,
                    'bbox': [x, y, x+w, y+h],
                    'timestamp': datetime.now().isoformat()
                })

            # Person detection
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                detections.append({
                    'class': 'person',
                    'confidence': 0.9,
                    'bbox': [x, y, x+w, y+h],
                    'timestamp': datetime.now().isoformat()
                })

            # Convert back to PIL Image for display
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result_image = Image.fromarray(img_rgb)

            return detections, result_image

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return [], image

    def update_detection_history(self, detections):
        """Update detection history with new detections"""
        self.detection_history.extend(detections)
        if len(self.detection_history) > self.max_history:
            self.detection_history = self.detection_history[-self.max_history:]

    def get_detection_statistics(self):
        """Get statistics from detection history"""
        if not self.detection_history:
            return {}

        stats = {
            'total_detections': len(self.detection_history),
            'vehicle_count': 0,
            'person_count': 0,
            'motion_events': 0,
            'hourly_activity': [0] * 24
        }

        for det in self.detection_history:
            hour = datetime.fromisoformat(det['timestamp']).hour
            stats['hourly_activity'][hour] += 1

            if det['class'] == 'vehicle':
                stats['vehicle_count'] += 1
            elif det['class'] == 'person':
                stats['person_count'] += 1
            elif det['class'] == 'motion':
                stats['motion_events'] += 1

        return stats

    def send_alert(self, image, detections, emailjs_user_id, template_id, service_id):
        """Send alert notification"""
        try:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            detection_text = []
            for det in detections:
                if det['class'] == 'vehicle':
                    text = f"Vehicle detected - Confidence: {det['confidence']:.2%}"
                    detection_text.append(text)
                elif det['class'] == 'person':
                    detection_text.append(f"Person detected - Confidence: {det['confidence']:.2%}")
                elif det['class'] == 'motion':
                    detection_text.append(f"Motion detected in zones: {det.get('zones', [])}")

            payload = {
                "service_id": service_id,
                "template_id": template_id,
                "user_id": emailjs_user_id,
                "template_params": {
                    "detection_results": "\n".join(detection_text),
                    "image": f"data:image/png;base64,{img_str}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }

            response = requests.post(
                "https://api.emailjs.com/api/v1.0/email/send",
                json=payload
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending alert: {str(e)}")
            return False