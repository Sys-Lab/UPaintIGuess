__author__ = 'Excelle'

from flask import Flask, render_template, request
from flask import jsonify, session, redirect, url_for, make_response
from config import config
from api import APIError, Player, dump_class
from flask.ext.socketio import SocketIO, send, emit
from flask.ext.socketio import join_room, leave_room
from flask.ext.sqlalchemy import SQLAlchemy
from random import randrange

import captcha
import re
import time

_RE_MD5 = re.compile(r'^[0-9a-fA-F]{32}$')
_RE_EMAIL = re.compile(r'^[\w\.\-]+@[\w\-]+(\.[\w\-]+){1,4}$')
_COOKIE_KEY = config.configs.session.secret
# This list includes routes that allow logined users only
login_requre_list = ['/room', '/main', '/logout', '/userinfo', '/editinfo',
                     '/changepasswd', '/contribute']
# Only visitors can login or register
visitor_only_list = ['/login', '/register']

app = Flask(__name__)
socketio = SocketIO(app)
players = dict()
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'a_usrs'
    t_uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_username = db.Column(db.String(32), nullable=False)
    t_password = db.Column(db.String(32), nullable=False)
    t_emailaddr = db.Column(db.String(128), nullable=False)
    t_gender = db.Column(db.Integer)
    t_privilege = db.Column(db.Integer, default=0)
    t_credits = db.Column(db.Integer, default=10)
    t_created_at = db.Column(db.Float, default=time.time())


class ExtInfo(db.Model):
    __tablename__ = 'a_usrext'
    t_uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_avatar = db.Column(db.String)
    t_motto = db.Column(db.String(80))
    t_qqid = db.Column(db.String(12))
    t_cellphone = db.Column(db.String(11))
    t_zipcode = db.Column(db.String(6))
    t_website = db.Column(db.String)
    t_birthday = db.Column(db.Float)


class Word(db.Model):
    __tablename__ = 'a_words'
    t_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_word = db.Column(db.String(16))
    t_desc = db.Column(db.String(24))


def get_current_user():
    user = None
    try:
        user = request.user
    except AttributeError:
        pass
    return user


@app.errorhandler(APIError)
def handle_api_error(error):
    '''
        API Error handler
    '''
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# This is a interceptor which will validate your login state.
# If you are requesting /room or /main with visitor identity,
# this function will redirect you to the homepage
#@app.before_request
def validate_login():
    # For visitors:
    user = None
    try:
        user = User.query.filter_by(t_emailaddr=session['email']).first()
    except KeyError:
        pass
    finally:
        if not user:
            for i in login_requre_list:
                if i == request.path:
                    return redirect(url_for('.index'))
        else:
            for i in visitor_only_list:
                if i == request.path:
                    return redirect(url_for('.index'))


# Front-end pages:
@app.route('/', methods=['GET'])
def index():
    return render_template('index_page.html', user=get_current_user())


@app.route('/room', methods=['GET'])
def select_room():
    return render_template('rooms.html', user=get_current_user())

@app.route('/main', methods=['GET'])
def game():
    return render_template('main.html', user=get_current_user())


@app.route('/register', methods=['GET'])
def register():

    cap, img_string=captcha.generate_captcha()
    return render_template('register.html')# here need to translate the img string to image


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/contribute', methods=['GET'])
def contribute_words():
    return render_template('words.html', user=get_current_user())


@app.route('/userinfo', methods=['GET'])
def display_user_info():
    return render_template('userinfo.html', user=get_current_user())


@app.route('/editinfo', methods=['GET'])
def edit_user_info():
    return render_template('editinfo.html', user=get_current_user())


@app.route('/changepasswd', methods=['GET'])
def change_password():
    return render_template('password.html', user=get_current_user())


# APIs
@app.route('/api/captcha', methods=['GET'])
def get_captcha():
    cap, img = captcha.generate_captcha()
    session['captcha'] = cap
    response = make_response(img.getvalue())
    response.headers['Content-Type'] = 'image/gif'
    return response


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
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        gender = request.form['gender']
        captcha = request.form['captcha'].strip()
        cap_answer = session['captcha']
        if captcha.lower() != cap_answer.lower():
            raise APIError('Wrong captcha.', 403)
        check_exist = User.query.filter_by(t_emailaddr=email).first()
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
        db.session.add(u)
        db.session.commit()
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
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        remember = request.form['remember'].strip()
        remember = int(remember)
        user = User.query.filter_by(t_emailaddr=email).first()
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


# Socket IO apis
@socketio.on('join')
def on_join(data):
    global players
    username = session['username']
    email = session['email']
    room = session['room']
    join_room(room)
    p = Player(username, email)
    if isinstance(players[room], list):
        players[room][0].append(p)
    else:
        players[room]= [[],None,None]
        players[room][0].append(p)
    send(username + ' has joined the group ' + room, room=room)
    emit('join',{'room':session['room']})

@socketio.on('join_room')
def re_join(data):
    session['room']=data['room']


@socketio.on('leave')
def on_leave(data):
    username = session['username']
    email = session['email']
    room = data['room']
    leave_room(room)
    if isinstance(players[room], list):
        for i in range(players[room][0].__len__()):
            if players[room][0][i].email == email:
                check_out_player(players[room][0].pop(i))
    send(username + ' has left the room.', room=room)


@socketio.on('ready')
def on_ready(data):
    global players
    username = session['username']
    email = session['email']
    room = data['room']
    send(username + ' is ready.', room=room)
    if isinstance(players[room], list):
        ready_to_go = True
        # Set current player ready
        for i in players[room][0]:
            if i.email == email:
                i.ready()
        # Query for whether all users are ready.
        for i in players[room][0]:
            if not i.ready():
                ready_to_go = False
    if ready_to_go:
        emit('ready',room=data['room'])
        pick_word(data['room'])
        emit('word',players[data['room']][1])


@socketio.on('draw')
def on_draw(data):
    print 'darw ok'
    emit('draw', data, room=data['room'])

@socketio.on('get_desc')
def on_get_desc(data):
    emit('msg',players[room][2], room=data['room'])


@socketio.on('msg')
def on_chat(data):
    global players
    room = data['room']
    # Check if guessed right. If so no display.
    if data['message'] == players[room][1]:
        if isinstance(players[room], list):
            for i in players[room][0]:
                if i.email == session['email']:
                    i.answer_ok()
                    i.add_points(3)
    else:
        emit('msg',session['username'] +':' + data['message'],
             json=False, room=data['room'])
        print 'send msg success'


@socketio.on('end')
def on_game_end(data):
    # Check out all players
    if isinstance(players[data['room']], list):
        for i in players[data['room']][0]:
            if i.username==session['username']:
                check_out_player(i)
                p=i
                break
    emit('message',session['username']+':'+chr(p.get_points()),room=data['room'])       

def pick_word(room):
    global players
    rows = Word.query.count()
    num = randrange(rows)
    word = Word.query.filter_by(t_id=num).first()
    players[room][1] = word['t_word']
    players[room][2] = word['t_desc']


def check_out_player(player):
    '''
        Check out a player
    '''
    # Get corresponding user object
    user = User.query.filter_by(t_emailaddr=player.email).first()
    user.t_credits += player.points
    user.update()

if __name__ == '__main__':
    db_user = config.configs.db.user
    db_pass = config.configs.db.password
    db_name = config.configs.db.database
    db_host = config.configs.db.host
    db_port = config.configs.db.port

    db_connection_str = 'mysql+mysqlconnector://' + db_user + ':' + db_pass + '@' + db_host + ':' + \
                        str(db_port) + '/' + db_name
    app.config['SQLALCHEMY_DATABASE_URI'] = db_connection_str
    app.config.from_object('config.config')
    socketio.run(app)
