from src import config, logger, functions, db_handler, users
from src import video_handler as vh
from src import audio_handler as ah
from flask import Flask, render_template, Response, request, jsonify, redirect, session, make_response
import threading


log = logger.Log('main')
mongo = db_handler.MongoDB('CamMGR')
app = Flask('CamMGR')
threads = {}
'''
1. text
https://www.geeksforgeeks.org/python-opencv-write-text-on-video/
2. audio
https://stackoverflow.com/questions/14140495/how-to-capture-a-video-and-audio-in-python-from-a-camera-or-webcam
'''


# Initialize sequence
def init():
    vh.init_vc()
    audio = ah.init_ac()
    # log.write('init complete')


# Main page
@app.route('/')
def index():
    # Validate logon and if session started
    user = users.validate_logon()
    if not user:
        return render_template('login.html')
    elif 'session' in user:
        if mongo.read_one('sessions', {'id': user['session'], 'status': {'$ne': 'Ended'}}):
            return redirect('/record')
    # Validate page param is a valid route
    # s = app.url_map.iter_rules()
    # urls = []
    # for i in s:
    #     urls.append(i.endpoint)
    # if 'page' in request.values:
    #     page = request.values['page']
    #     if page in urls:
    #         return redirect('/{}'.format(page))
    #     return redirect('/')
    # vh.cams[0].release()  # todo: remove after session validate complete
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.form:
        return users.login(request.form)
    return redirect('/')


# Settings page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # Validate logon and if session started
    user = users.validate_logon()
    if not user:
        return redirect('/')
    elif 'session' in user:
        return redirect('/record')
    # todo: add Settings for each user
    # Setting update
    if request.form:
        req_f = dict(request.form)
        for k in req_f:
            mongo.update_one('settings', {'settings': {'$exists': True}}, {'settings.{}.value'.format(k): req_f[k]})
    # Read settings
    sets = mongo.read_one('settings', {'settings': {'$exists': True}})
    if sets:
        sets = sets['settings']
    return render_template('settings.html', settings=sets)


# Record session page
@app.route('/record', methods=['GET', 'POST'])
def record():
    # Validate logon and if session started
    user = users.validate_logon()
    if not user:
        return redirect('/')
    # Record handling (start, stop... )
    if 'func' in request.values:
        functions.run(dict(request.values), user)
        return redirect('/record')
    # Get session info if
    elif 'session' in user:
        rec_session = mongo.read_one('sessions', {'id': user['session']})
        if not rec_session:
            users.update_user({'session': ''}, '$unset')
        elif rec_session['status'] != 'Ended':
            return render_template('record.html', session=rec_session)
        else:
            users.update_user({'session': ''}, '$unset')
    if request.form:
        ses_id = functions.ts()
        s_name = request.form['session_name']
        new_ses = {'id': ses_id, 'folder_dir': ses_id, 'file_name': s_name, 'status': 'init'
                   , 'cams': [0], 'comments': []}  # todo: comment:{'ts', 'comment'}
        new_ses.update(dict(request.form))
        mongo.write('sessions', new_ses)
        users.update_user({'session': ses_id})
        return redirect('/record')
    return render_template('new_session.html')


# History viewer page
@app.route('/history')
def history():
    # Validate logon and if session started
    user = users.validate_logon()
    if not user:
        return redirect('/')
    elif 'session' in user:
        return redirect('/record')
    hist = mongo.read_all('sessions', {'finished': {'$exists': True}})
    return render_template('history.html', history=hist)


# Stream request path
@app.route('/video_feed')
def video_feed():
    user = users.validate_logon()
    if user:
        req_vals = dict(request.values)
        if 'index' in req_vals:
            if req_vals['index'].isnumeric():
                return Response(vh.video_stream(int(req_vals['index'])),
                                mimetype= 'multipart/x-mixed-replace;boundary=frame')
    return Response()


def start_rec(session_data):
    threads[session_data['id']] = []
    i = 0
    for cam_adr in session_data['cams']:
        cam = vh.cams[cam_adr]
        file_name = '{}_{}'.format(session_data['file_name'], i)
        threads[session_data['id']].append(threading.Thread(target=vh.cam_capture, args=(session_data['id'], cam, file_name)))
        threads[session_data['id']][i].start()
        i += 1


# Run main routine
if __name__ == '__main__':
    # log.write('app started')
    init()
    app.secret_key ='$%^KJBKJN$$lmnlmn#'
    app.run(host='0.0.0.0', debug=True)

