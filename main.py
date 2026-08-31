import cv2
import mediapipe as mp
from collections import deque, Counter

# MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Camera
cap = cv2.VideoCapture(0)

# Smooth detection
history = deque(maxlen=7)


def get_fingers(hand):
    lm = hand.landmark

    # Index, Middle, Ring, Pinky
    fingers = [
        1 if lm[8].y < lm[6].y else 0,
        1 if lm[12].y < lm[10].y else 0,
        1 if lm[16].y < lm[14].y else 0,
        1 if lm[20].y < lm[18].y else 0
    ]

    return fingers


def recognize_gesture(hand):
    lm = hand.landmark
    fingers = get_fingers(hand)

    index, middle, ring, pinky = fingers

    # Distance between thumb and index
    thumb_index_distance = (
        (lm[4].x - lm[8].x) ** 2 +
        (lm[4].y - lm[8].y) ** 2
    ) ** 0.5

    # -------------------------
    # OK 👌
    # -------------------------
    if (
        thumb_index_distance < 0.08
        and middle
        and ring
        and pinky
    ):
        return "OK"

    # -------------------------
    # Open Palm 🖐️
    # -------------------------
    if all(fingers) and lm[4].y < lm[3].y:
        return "Open Palm"

    # -------------------------
    # Peace ✌️
    # -------------------------
    if index and middle and not ring and not pinky:
        return "Peace"

    # -------------------------
    # Pointing ☝️
    # -------------------------
    if index and not middle and not ring and not pinky:
        return "Pointing"
    if index and not middle and not ring and pinky:
        return "yoo-yo"

    # -------------------------
    #  Phone Call 🤙
    # -------------------------
    if pinky and not index and not middle and not ring:
        return " phone Call"

    # -------------------------
    # Thumb gestures 👍 👎
    # -------------------------
    if not index and not middle and not ring and not pinky:

        # Thumb pointing upward
        if lm[4].y < lm[2].y:
            return "Thumbs Up"

        # Thumb pointing downward
        else:
            return "Thumbs Down"

    # -------------------------
    # Fist ✊
    # -------------------------
    if not index and not middle and not ring and not pinky:
        return "Fist"

    return "Unknown"


while True:

    success, frame = cap.read()

    if not success:
        break

    # Mirror camera
    frame = cv2.flip(frame, 1)

    # Convert BGR → RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process hand
    results = hands.process(rgb)

    gesture = "No Hand"

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]

        # Draw landmarks
        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )

        # Recognise
        current = recognize_gesture(hand)

        # Smooth detection
        history.append(current)

        if len(history) >= 4:
            gesture = Counter(history).most_common(1)[0][0]
        else:
            gesture = current

    else:
        history.clear()

    # Display
    cv2.putText(
        frame,
        "HAND GESTURE RECOGNITION",
        (10, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Gesture: {gesture}",
        (10, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        "ESC = Exit",
        (10, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.imshow("Hand Gesture Recognition", frame)

    # Exit
    if cv2.waitKey(1) & 0xFF == 27:
        break


cap.release()
cv2.destroyAllWindows()
hands.close()