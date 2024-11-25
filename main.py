from src import config, logger
from src.camera_handler import CamThread
from flask import Flask, render_template, Response, request, jsonify
import cv2
import json
import uuid
import asyncio
import logging
import time

video = []
app = Flask('CamMGR')

'''
1. text
https://www.geeksforgeeks.org/python-opencv-write-text-on-video/
'''


def init():
    # todo: init all streams from config
    video.append(cv2.VideoCapture(0))


@app.route('/')
def index():
    return render_template('index.html')


def video_stream(idx):
    if idx >= len(video):
        return
    while True:
        ret, frame = video[idx].read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpeg',frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    req_vals = dict(request.values)
    if 'index' not in req_vals:
        return Response()
    elif not req_vals['index'].isnumeric():
        return Response()
    return Response(video_stream(int(req_vals['index'])), mimetype= 'multipart/x-mixed-replace;boundary=frame')


if __name__ == '__main__':
    init()
    app.run(host='0.0.0.0', debug=True)

