import cv2
from flask import Flask, render_template, Response, send_from_directory
import threading
import os
import datetime
import time
import numpy as np

app = Flask(__name__)
video_capture = cv2.VideoCapture(0)
frames = []
lock = threading.Lock()

def record_video():
    global frames
    while True:
        ret, frame = video_capture.read()
        with lock:
            frames.append(frame)

        # Limit the recording to the last 10 minutes
        if len(frames) > 600:
            with lock:
                frames = frames[-600:]

        time.sleep(1/30)  # Sleep for ~33ms to achieve approximately 30 frames per second

def generate_frames():
    global frames
    while True:
        if len(frames) == 0:
            continue

        with lock:
            frame = frames[-1]

        ret, encoded_frame = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame.tobytes() + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_locally')
def save_locally():
    global frames
    if len(frames) > 0:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"nagranie-z{timestamp}.mp4"
        save_path = os.path.join(os.getcwd(), 'records', filename)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(save_path, fourcc, 30, (frames[0].shape[1], frames[0].shape[0]))

        with lock:
            for frame in frames:
                out.write(frame)

        out.release()
        return f"Recording saved as {filename} on the server."
    else:
        return 'No frames to save.'

@app.route('/save_on_server')
def save_on_server():
    global frames
    if len(frames) > 0:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"nagranie-z{timestamp}.mp4"
        save_path = os.path.join(os.getcwd(), 'nagrania', filename)
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(save_path, fourcc, 30, (frames[0].shape[1], frames[0].shape[0]))

        with lock:
            for frame in frames:
                out.write(frame)

        out.release()
        return send_from_directory(os.path.dirname(save_path), filename, as_attachment=True)
    else:
        return 'No frames to save.'

if __name__ == '__main__':
    threading.Thread(target=record_video).start()
    app.run(host='0.0.0.0', port=419)
