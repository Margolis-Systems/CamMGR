import main
import secrets
from datetime import datetime, timedelta


def login(req):
    if 'username' in req and 'password' in req:
        user = main.mongo.read_one('users', {'username': req['username'], 'password': req['password']})
        if user:
            token = secrets.token_hex(16)
            update_user({'token': token})
            user['token'] = token
            main.session['user'] = user
            main.session.modified = True
            resp = main.make_response()
            resp.headers['location'] = '/'
            expire_date = datetime.now() + timedelta(days=3)
            resp.set_cookie('token', token, expires=expire_date)
            resp.set_cookie('username', user['username'], expires=expire_date)
            return resp, 302
    else:
        secret_token = main.request.cookies.get('token')
        username = main.request.cookies.get('username')
        if username and secret_token:
            user = main.mongo.read_one('users', {'username': username, 'token': secret_token})
            if user:
                token = secrets.token_hex(16)
                update_user({'token': token})
                user['token'] = token
                main.session['user'] = user
                main.session.modified = True
    return main.redirect('/')


def validate_logon():
    if 'user' in main.session:
        user = main.mongo.read_one('users', {'username': main.session['user']['username'],
                                             'token': main.session['user']['token']})
        if user:
            return user
    return {}


def update_user(user_data, opr='$set'):
    main.mongo.update_one('users', {'username': main.session['user']['username']}, user_data, opr)
