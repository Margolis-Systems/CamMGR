import main
from datetime import datetime, timedelta


def run(cmd, user):
    func = cmd['func']
    if func == 'start':
        if 'session' in user:
            rec_session = main.mongo.read_one('sessions', {'id': user['session'], 'status': {'$nin': ['Started', 'Ended']}})
            if rec_session:
                to = datetime.now() + timedelta(minutes=int(rec_session['duration']))
                main.mongo.update_one('sessions', {'id': user['session']}, {'status': 'Started', 'timeout': to,
                                                                            'start_ts': datetime.now()})
                main.start_rec(rec_session)
    elif func == 'stop':
        main.mongo.update_one('sessions', {'id': user['session']}, {'timeout': datetime.now(), 'end_ts': datetime.now(), 'status': 'Ended'})
        main.users.update_user({'session': ''}, '$unset')
    elif func == 'reset':
        main.vh.init_vc()
    return


def ts():
    return datetime.now().strftime('%Y%m%d_%H%M%S')
