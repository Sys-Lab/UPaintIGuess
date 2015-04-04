__author__ = 'Excelle'

from flask import Flask, render_template, request
from flask import jsonify, session, redirect, url_for
from config import config
from api import APIError, Player, dump_class
from db import db_session
from model import User, ExtInfo, Word
from flask.ext.socketio import SocketIO, send, emit
from flask.ext.socketio import join_room, leave_room
from random import randrange

import captcha
import re

_RE_MD5 = re.compile(r'^[0-9a-fA-F]{32}$')
_RE_EMAIL = re.compile(r'^[\w\.\-]+@[\w\-]+(\.[\w\-]+){1,4}$')
_COOKIE_KEY = config.configs.session.secret

app = Flask(__name__)
socketio = SocketIO(app)
players = dict()


@app.errorhandler(APIError)
def handle_api_error(error):
    '''
        API Error handler
    '''
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.before_request()
def validate_login():
    if request.url != '/':
        user = User.query().filter(User.t_emailaddr == session['email']).first()
        if user:
            if user.t_password == session['password']:
                return
        return redirect(url_for('/'))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', user=request.user)


@app.route('/room', methods=['GET'])
def select_room():
    return render_template('rooms.html', user=request.user)


@app.route('/main', methods=['GET'])
def game():
    return render_template('main.html', user=request.user)


def contribute_words():
    return render_template('words.html', user=request.user)


@app.route('/api/captcha', methods=['GET'])
def get_captcha():
    cap, img = captcha.generateCaptcha()
    session['captcha'] = cap
    return img.getvalue()


@app.route('/api/register', methods=['POST'])
def api_register():
    '''
    User registration API
    Required HTTP Method: POST
    Required data:
        1. username - User's nickname
        2. email    - Email address !CAUTION: UNIQUE CREDENTIAL FOR USERS!
        3. password - Password should be sent MD5 hashed
        4. gender   - 0 for girls and 1 for boys
        5. captcha
    '''
    try:
        username = request['username'].strip()
        email = request['email'].strip().lower()
        password = request['password'].strip()
        gender = request['gender']
        captcha = request['captcha'].strip()
        cap_answer = session['captcha']
        if captcha.lower() != cap_answer.lower():
            raise APIError('Wrong captcha.', 403)
        check_exist = User.query().filter(User.t_emailaddr == email).first()
        if check_exist:
            raise APIError('Email address has been registered.', 400)
        if not _RE_MD5.match(password):
            raise APIError('Invalid password format', 400)
        if not _RE_EMAIL.match(email):
            raise APIError('Invalid email address', 400)
        if not username.strip():
            raise APIError('Empty username', 400)
        if not gender:
            raise APIError('A gender should be selected', 400)
        u = User()
        u.t_username = username
        u.t_emailaddr = email
        u.t_password = password
        u.t_gender = int(gender)
        ext = ExtInfo()
        ext.t_uid = u.t_uid
        if u.t_gender:
            ext.t_avatar = '/static/images/avatar_default_boy.png'
        else:
            ext.t_avatar = '/static/images/avatar_default_girl.png'
        db_session.add(u)
        db_session.add(ext)
        db_session.commit()
        session['email'] = u.t_emailaddr
        session['username'] = u.t_username
        session['password'] = u.t_password
        request.user = u
        return dump_class(u)
    except KeyError, ex:
        raise APIError(ex.message, 500)


@app.route('/api/auth', methods=['POST'])
def api_authenticate():
    try:
        email = request['email'].strip().lower()
        password = request['password'].strip()
        remember = request['remember'].strip()
        remember = int(remember)
        user = User.query().filter(User.t_emailaddr == email).first()
        if not user:
            raise APIError('User does not exist', 400)
        if not user.t_password == password:
            raise APIError('Wrong password', 400)
        if remember:
            session.permanent = True
        session['email'] = user.t_emailaddr
        session['username'] = user.t_username
        session['password'] = user.t_password
        request.user = user
        user.t_password = '******'
        return dump_class(user)
    except KeyError, e:
        raise APIError(e.message, 500)


@app.route('/api/logout', methods=['GET'])
def api_logout():
    session.permanent = False
    session.pop('username', None)
    session.pop('email', None)
    session.pop('password', None)
    request.user = None
    return redirect(url_for('/'))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@socketio.on('join')
def on_join(data):
    global players
    username = session['username']
    email = session['email']
    room = data['room']
    join_room(room)
    p = Player(username, email)
    if isinstance(players[room], list):
        players[room].append(p)
    else:
        players[room] = [p]
    send(username + ' has joined the group ' + room, room=room)


@socketio.on('leave')
def on_leave(data):
    username = session['username']
    email = session['email']
    room = data['room']
    leave_room(room)
    if isinstance(players[room], list):
        for i in range(players[room].__len__()):
            if players[room][i].email == email:
                check_out_player(players[room].pop(i))
    send(username + ' has left the room.', room=room)


@socketio.on('ready')
def on_ready(data):
    username = session['username']
    email = session['email']
    room = data['room']
    send(username + ' is ready.', room=room)
    if isinstance(players[room], list):
        ready_to_go = True
        # Set current player ready
        for i in players[room]:
            if i.email == email:
                i.ready()
        # Query for whether all users are ready.
        for i in players[room]:
            if not i.ready():
                ready_to_go = False
    if ready_to_go:
        return redirect(url_for('/main'))


@socketio.on('draw')
def on_draw(data):
    emit('draw', data['point'], room=data['room'])


@socketio.on('get_word')
def on_get_word(data):
    '''
        Get a word from the database randomly
    '''
    pick_word()
    send(session['word'], room=data['room'])


@socketio.on('get_desc')
def on_get_desc(data):
    send(session['word_desc'], room=data['room'])


@socketio.on('msg')
def on_chat(data):
    room = data['room']
    # Check if guessed right. If so no display.
    if data['message'] == session['word']:
        if isinstance(players[room], list):
            for i in players[room]:
                if i.email == session['email']:
                    i.answer_ok()
                    i.add_points(3)
    else:
        send(data['username'] + ':' + data['message'],
             json=False, room=data['room'])


@socketio.on('end')
def on_game_end(data):
    # Check out all players
    if isinstance(players[data['room']], list):
        for i in players[data['room']]:
            check_out_player(i)
    return players.pop(data['room'])


def pick_word():
    rows = Word.query().count()
    num = randrange(rows)
    word = Word.query().filter(Word.t_id == num).first()
    session['word'] = word['t_word']
    session['word_desc'] = word['t_desc']


def check_out_player(player):
    '''
        Check out a player
    '''
    # Get corresponding user object
    user = User.query().filter(User.t_emailaddr == player.email).first()
    user.t_credits += player.points
    user.update()


if __name__ == '__main__':
    app.config.from_object('config.config')
