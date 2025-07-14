import cv2
import mediapipe as mp
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

# --- Add fingers_up function ---
def fingers_up(hand_landmarks):
    tip_ids = [4, 8, 12, 16, 20]  # thumb to pinky
    fingers = []

    # Thumb — compare x-coordinates (horizontal)
    if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x:
        fingers.append(1)  # Thumb is up
    else:
        fingers.append(0)  # Thumb is down

    # Fingers — compare y-coordinates (vertical)
    for id in range(1, 5):
        if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y:
            fingers.append(1)  # Finger is up
        else:
            fingers.append(0)  # Finger is down

    return fingers

# Load Spotify credentials from environment variables
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
))

mp_hands = mp.solutions.hands
hand = mp_hands.Hands()

mp_drawings = mp.solutions.drawing_utils

# --- Gesture to action mapping ---
last_gesture = None
last_action_time = 0
cooldown = 1.5  # seconds
neutral_gesture = [0, 0, 0, 0, 0]
gesture_ready = True  # Only trigger when coming from neutral

def gesture_to_action(finger_states):
    # Map gestures to Spotify actions
    if finger_states == [0, 1, 0, 0, 0]:
        return 'next'
    elif finger_states == [0, 1, 1, 0, 0]:
        return 'previous'
    elif finger_states == [0, 0, 0, 0, 0]:
        return 'pause'
    elif finger_states == [0, 1, 1, 1, 1]:
        return 'play'
    else:
        return None

while True:
    success, frame = cap.read()
    if success:
        RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hand.process(RGB_frame)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawings.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                finger_states = fingers_up(hand_landmarks)
                print("Fingers up:", finger_states)
                gesture = gesture_to_action(finger_states)
                current_time = time.time()
                # Only trigger if gesture_ready (i.e., last gesture was neutral)
                if gesture and gesture != 'pause' and gesture_ready:
                    if gesture == 'next':
                        try:
                            sp.next_track()
                            print("Next track!")
                        except Exception as e:
                            print("Error skipping track:", e)
                    elif gesture == 'previous':
                        try:
                            sp.previous_track()
                            print("Previous track!")
                        except Exception as e:
                            print("Error going to previous track:", e)
                    elif gesture == 'play':
                        try:
                            sp.start_playback()
                            print("Play!")
                        except Exception as e:
                            print("Error starting playback:", e)
                    last_gesture = gesture
                    last_action_time = current_time
                    gesture_ready = False  # Block until neutral
                elif finger_states == neutral_gesture:
                    gesture_ready = True  # Reset trigger when hand is neutral
                    # Optionally, handle pause here (if you want pause to be edge-triggered too)
                    if gesture == 'pause' and (last_gesture != 'pause' or (current_time - last_action_time) > cooldown):
                        try:
                            sp.pause_playback()
                            print("Pause!")
                        except Exception as e:
                            print("Error pausing playback:", e)
                        last_gesture = 'pause'
                        last_action_time = current_time
        cv2.imshow("capture image", frame)
        if cv2.waitKey(1) & 0xFF == ord(" "):
            break

cap.release()
cv2.destroyAllWindows()