from datetime import datetime, timedelta
from src import logger
import cv2
import main
import os


log = logger.Log('video_handler')
cams = []


def init_vc():
    cams_conf = main.mongo.read_all('settings', {'camera': {'$exists': True}})
    for c in cams_conf:
        log.write('init: {}'.format(c['camera']['port']))
        cams.append(cv2.VideoCapture(c['camera']['port']))
    return cams


def cam_capture(session_id, cam, file_name):
    rec_session = main.mongo.read_one('sessions', {'id': session_id})
    if not rec_session:
        return
    folder = rec_session['folder_dir']
    log.write('Start capture. file: {}/{}'.format(folder, file_name))
    frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    if not os.path.exists('sessions/{}'.format(folder)):
        os.mkdir('sessions/{}'.format(folder))
    out = cv2.VideoWriter('sessions/{}/{}.mp4'.format(folder, file_name), fourcc, 15.0, (frame_width, frame_height))
    if cam.isOpened():
        ret, frame = cam.read()
        log.write('Frame capture. file: {}/{}'.format(folder, file_name))
    else:
        ret = False
        log.write('No frame capture. file: {}/{}'.format(folder, file_name))

    while ret:
        rec_session = main.mongo.read_one('sessions', {'id': session_id})
        to = rec_session['timeout']
        ret, frame = cam.read()
        frame = cv2.flip(frame, 1)
        out.write(frame)
        if datetime.now() >= to:
            log.write('Finish capture. file: {}/{}'.format(folder, file_name))
            main.mongo.update_one('sessions', {'id': session_id}, {'end_ts': datetime.now(), 'status': 'Ended'})
            break
    log.write('Interrupted capture. file: {}/{}'.format(folder, file_name))


# Stream function
def video_stream(cam_idx):
    cam = cams[cam_idx]
    while True:
        ret, frame = cam.read()
        frame = cv2.flip(frame, 1)  # todo: flip from config
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpeg',frame)
            frame = buffer.tobytes()
            yield b'--frame\r\n' b'Content-type: image/jpeg\r\n\r\n' + frame + b'\r\n'

