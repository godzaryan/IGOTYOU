import cv2
import mediapipe as mp
import threading
import pyautogui
import time
import math

class GestureController:
    def __init__(self, debug=False):
        self.debug = debug
        self.running = True
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.current_gesture = None
        self.last_action_time = 0
        self.debounce_time = 1.0
        self.swipe_threshold = 0.05
        self.smooth_factor = 0.3
        self.screen_width, self.screen_height = pyautogui.size()
        self.frame = None
        self.lock = threading.Lock()
        self.start_pos = None
        self.is_controlling_cursor = False
        self.prev_cursor_x = 0
        self.prev_cursor_y = 0

    def start(self):
        gesture_thread = threading.Thread(target=self.run, daemon=True)
        gesture_thread.start()

        cursor_control_thread = threading.Thread(target=self.control_cursor, daemon=True)
        cursor_control_thread.start()

    def stop(self):
        self.running = False

    def run(self):
        cap = cv2.VideoCapture(0)

        while self.running:
            success, frame = cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            with self.lock:
                self.frame = rgb_frame

            results = self.hands.process(rgb_frame)

            hand_present = (
                results.multi_hand_landmarks is not None and
                results.multi_handedness and
                results.multi_handedness[0].classification[0].score > 0.8
            )

            if hand_present:
                hand_landmarks = results.multi_hand_landmarks[0]
                if self.debug:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                detected_gesture = self.detect_gesture(hand_landmarks)

                if detected_gesture:
                    self.verify_and_execute_gesture(detected_gesture)

            if self.debug:
                cv2.imshow("Gesture Detection", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

        cap.release()
        cv2.destroyAllWindows()

    def detect_gesture(self, hand_landmarks):
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]

        is_index_open = index_tip.y < hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
        is_middle_open = middle_tip.y < hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
        is_ring_open = ring_tip.y < hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP].y
        is_pinky_open = pinky_tip.y < hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP].y

        if is_index_open and is_middle_open and is_ring_open and is_pinky_open:
            current_pos = index_tip.x
            if self.start_pos is None:
                self.start_pos = current_pos

            movement = current_pos - self.start_pos

            if movement > self.swipe_threshold:
                self.start_pos = None
                return "swipe_right"
            elif movement < -self.swipe_threshold:
                self.start_pos = None
                return "swipe_left"

        if is_index_open and not is_middle_open and not is_ring_open and not is_pinky_open:
            return "cursor_control"

        if is_index_open and is_middle_open and is_ring_open and is_pinky_open:
            return "exit_cursor_control"

        return None

    def verify_and_execute_gesture(self, gesture):
        current_time = time.time()

        if current_time - self.last_action_time < self.debounce_time:
            return

        if gesture == "swipe_right":
            pyautogui.hotkey("alt", "tab")
            print("Switched to next window")
        elif gesture == "swipe_left":
            pyautogui.hotkey("alt", "shift", "tab")
            print("Switched to previous window")
        elif gesture == "cursor_control":
            self.is_controlling_cursor = True
            print("Cursor control started")
        elif gesture == "exit_cursor_control":
            self.is_controlling_cursor = False
            print("Exited cursor control")

        self.last_action_time = current_time

    def control_cursor(self):
        while self.running:
            if not self.is_controlling_cursor:
                time.sleep(0.01)
                continue

            with self.lock:
                if self.frame is None:
                    continue
                results = self.hands.process(self.frame)

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]

                cursor_x = int(self.screen_width * index_tip.x)
                cursor_y = int(self.screen_height * index_tip.y)

                smoothed_x = int(self.prev_cursor_x + (cursor_x - self.prev_cursor_x) * self.smooth_factor)
                smoothed_y = int(self.prev_cursor_y + (cursor_y - self.prev_cursor_y) * self.smooth_factor)

                pyautogui.moveTo(smoothed_x, smoothed_y)
                self.prev_cursor_x, self.prev_cursor_y = smoothed_x, smoothed_y

                # Check for exit condition while in cursor control mode
                if self.detect_gesture(hand_landmarks) == "exit_cursor_control":
                    self.is_controlling_cursor = False
                    print("Exited cursor control due to exit gesture")

            time.sleep(0.01)

    def update(self):
        while self.running:
            time.sleep(0.1)


# Example usage
controller = GestureController(debug=False)
controller.start()

try:
    while True:
        controller.update()
except KeyboardInterrupt:
    controller.stop()
    print("Gesture detection stopped.")
