from src import config, logger
from src.camera_handler import CamThread
from flask import Flask, render_template, Response, request, jsonify
import cv2
import json
import uuid
import asyncio
import logging
import time

video = cv2.VideoCapture(0)
app = Flask('CamMGR')
kill = False


# def main():
#     thread = []
#     # err_log = logger.Log('errors')
#     for i in range(len(config.cameras)):
#         thread.append(CamThread(config.cameras[i]))
#         thread[i].start()


def generate_frames():
    camera = cv2.VideoCapture(0) # ==============IMPORTANT============
    while True:
        start_time = time.time()
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # concat frame one by one and show result
            yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            elapsed_time = time.time() - start_time
            logging.debug(f"Frame generation time: {elapsed_time} seconds")


@app.route('/')
def index():
    global kill
    kill = True
    req_vals = dict(request.values)
    print(req_vals)
    if 'index' in req_vals:
        stream_index = req_vals['index']
        kill = False
        print('i')
    return render_template('index.html')


def video_stream():
    global kill
    print(kill)
    while kill:
        ret, frame = video.read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpeg',frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype= 'multipart/x-mixed-replace;boundary=frame')


# @app.route('/stop')
# def stop_stream(stream_index=''):
#     if not stream_index:
#         req_vals = dict(request.values)
#         if 'index' in req_vals:
#             stream_index = req_vals['index']
#             main.thread[stream_index].stop()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # main()

'''
1. text
https://www.geeksforgeeks.org/python-opencv-write-text-on-video/
2. multi cams display
https://stackoverflow.com/questions/69495109/show-multiple-cameras-in-one-window
3. webhost
https://medium.com/@supersjgk/building-a-live-streaming-app-using-flask-opencv-and-webrtc-8cc8b521fa44
pip install aiohttp==3.9.0b0 
'''

