# Spotify Hand Gesture Controller

Control Spotify playback using your webcam and hand gestures

## Features
- Detects hand gestures using your webcam
- Maps gestures to Spotify actions (play, pause, next, previous)
- Uses OpenCV, MediaPipe, and Spotipy

## Requirements
- Python 3.8+
- Webcam
- Spotify Premium account (required for playback control)

## Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the `Spotify_controlller` directory with your Spotify API credentials:
   ```env
   SPOTIPY_CLIENT_ID=your_client_id
   SPOTIPY_CLIENT_SECRET=your_client_secret
   SPOTIPY_REDIRECT_URI=http://127.0.0.1:8080/callback
   ```
4. Run the main script:
   ```bash
   python main.py
   ```

## Controls
- **Quit:** Press the spacebar in the video window to exit the program.

## Hand Gestures
| Gesture (Fingers Up) | Action           |
|----------------------|------------------|
| [0, 1, 0, 0, 0]      | Next track       |
| [0, 1, 1, 0, 0]      | Previous track   |
| [0, 0, 0, 0, 0]      | Pause playback   |
| [0, 1, 1, 1, 1]      | Play/resume      |

- Each gesture is a list: [thumb, index, middle, ring, pinky] (1=up, 0=down)
- Return to a neutral pose (fist) before repeating a gesture.