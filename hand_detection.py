import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, List, Dict

class HandDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

    def get_finger_state(self, hand_landmarks) -> Dict[str, bool]:
        """Determine if each finger is extended"""
        finger_tips = {
            'thumb': (4, 3, 2),
            'index': (8, 7, 6),
            'middle': (12, 11, 10),
            'ring': (16, 15, 14),
            'pinky': (20, 19, 18)
        }

        states = {}
        for finger, (tip, mid, base) in finger_tips.items():
            if finger == 'thumb':
                # Special case for thumb
                extended = hand_landmarks.landmark[tip].x > hand_landmarks.landmark[mid].x
            else:
                # For other fingers, check if tip is higher than base
                extended = hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y

            states[finger] = extended

        return states

    def detect_gesture(self, hand_landmarks) -> str:
        """Enhanced gesture detection with multiple patterns"""
        finger_states = self.get_finger_state(hand_landmarks)

        # Define gesture patterns
        if all(finger_states.values()):
            return "OPEN_HAND"
        elif not any(finger_states.values()):
            return "CLOSED_FIST"
        elif finger_states['index'] and not any(v for k, v in finger_states.items() if k != 'index'):
            return "POINTING"
        elif finger_states['index'] and finger_states['middle'] and not any(v for k, v in finger_states.items() if k not in ['index', 'middle']):
            return "PEACE"
        elif finger_states['thumb'] and finger_states['pinky'] and not any(v for k, v in finger_states.items() if k not in ['thumb', 'pinky']):
            return "CALL"
        elif finger_states['thumb'] and not any(v for k, v in finger_states.items() if k != 'thumb'):
            return "THUMBS_UP"
        elif not finger_states['thumb'] and all(v for k, v in finger_states.items() if k != 'thumb'):
            return "FOUR_FINGERS"
        else:
            return "UNKNOWN"

    def detect_hands(self, frame):
        """Detect hands in the frame and return processed image with landmarks"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        gestures = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

                # Detect gesture
                gesture = self.detect_gesture(hand_landmarks)
                gestures.append(gesture)

                # Display gesture
                cv2.putText(
                    frame,
                    f"Gesture: {gesture}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

        return frame, gestures

    def calculate_hand_angle(self, hand_landmarks) -> float:
        """Calculate the angle of the hand relative to vertical"""
        wrist = hand_landmarks.landmark[0]
        middle_tip = hand_landmarks.landmark[12]

        angle = np.degrees(np.arctan2(
            middle_tip.y - wrist.y,
            middle_tip.x - wrist.x
        ))
        return angle