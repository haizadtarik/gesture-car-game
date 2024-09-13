import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)
draw_landmarks = mp.solutions.drawing_utils

last_position = None

def check_movement(hand_landmarks):
    global last_position
    
    media_x = round(sum([landmark.x for landmark in hand_landmarks.landmark]) / len(hand_landmarks.landmark), 2)
    
    if last_position is not None:
        if media_x < last_position:
            print("Moving left")
        elif media_x > last_position:
            print("Moving right")
    
    last_position = media_x

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    image_rgb = cv2.flip(image_rgb, 1)
    frame = cv2.flip(frame, 1)

    results = hands.process(image_rgb)

    if results.multi_hand_landmarks:
        # ------ draw all key points -----
        # for hand_landmarks in results.multi_hand_landmarks:
            # draw_landmarks.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # check_movement(hand_landmarks)

        # individual key
        for i in range(len(results.multi_hand_landmarks[0].landmark)):
            point = results.multi_hand_landmarks[0].landmark[i]
            x = int(point.x*frame.shape[0])
            y = int(point.y*frame.shape[1])
            # frame = cv2.circle(frame, (x,y), radius=5, color=(0, 0, 255), thickness=-1)
            frame = cv2.putText(frame, str(i), (x,y), 0, 1, (0,0,255), 1)

    cv2.imshow('Hand movement detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()