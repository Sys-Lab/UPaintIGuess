import captcha
import re
import time
import hashlib
import traceback
from flask import Flask, render_template, request, jsonify
from flask import session, redirect, url_for, make_response
from config import config
from api import APIError, Player, datetime_filter
from flask.ext.socketio import SocketIO, send, emit
from flask.ext.socketio import join_room, leave_room
from flask.ext.sqlalchemy import SQLAlchemy
from random import randrange
from base64 import b64decode


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

    def getDict(self):
        return dict(t_uid=self.t_uid, t_username=self.t_username,
                    t_password=self.t_password, t_emailaddr=self.t_emailaddr,
                    t_gender=self.t_gender, t_privilege=self.t_gender,
                    t_credits=self.t_gender, t_created_at=self.t_created_at)


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

    def getDict(self):
        return dict(t_uid=self.t_uid, t_avatar=self.t_avatar,
                    t_motto=self.t_motto, t_qqid=self.t_qqid,
                    t_cellphone=self.t_cellphone, t_zipcode=self.t_zipcode,
                    t_website=self.t_website, t_birthday=self.t_birthday)


class Word(db.Model):
    __tablename__ = 'a_words'
    t_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_word = db.Column(db.String(16))
    t_desc = db.Column(db.String(24))

    def getDict(self):
        return dict(t_id=self.t_id, t_word=self.t_word, t_desc=self.t_desc)


def get_current_user():
    user = None
    try:
        user = User.query.filter_by(t_emailaddr=session['email']).first()
    except AttributeError:
        pass
    except KeyError:
        pass
    print user
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
@app.before_request
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


@app.route('/main/<room>', methods=['GET'])
def game(room):
    print 'ok'
    session['room'] = room
    return render_template('main.html', user=get_current_user())


@app.route('/register', methods=['GET'])
def register():
    cap, img_string = captcha.generate_captcha()
    return render_template('register.html')


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/contribute', methods=['GET'])
def contribute_words():
    return render_template('words.html', user=get_current_user())


@app.route('/userinfo', methods=['GET'])
def display_user_info():
    u = get_current_user()
    ext = None
    if u:
        ext = ExtInfo.query.filter_by(t_uid=u.t_uid).first()
    return render_template('userinfo.html', user=u, usrext=ext)


@app.route('/editinfo', methods=['GET'])
def edit_user_info():
    u = get_current_user()
    ext = None
    if u:
        ext = ExtInfo.query.filter_by(t_uid=u.t_uid).first()
    return render_template('editinfo.html', user=u, usrext=ext)


@app.route('/changepasswd', methods=['GET'])
def change_password():
    return render_template('password.html', user=get_current_user())

#@app.route('/room',methods=['GET'])
#    return render_template('rooms.html',user=get_current_user())

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
            raise APIError('Wrong captcha.', 200)
        check_exist = User.query.filter_by(t_emailaddr=email).first()
        if check_exist:
            raise APIError('Email address has been registered.', 200)
        if not _RE_MD5.match(password):
            raise APIError('Invalid password format', 200)
        if not _RE_EMAIL.match(email):
            raise APIError('Invalid email address', 200)
        if not username.strip():
            raise APIError('Empty username', 200)
        if not gender:
            raise APIError('A gender should be selected', 200)
        u = User()
        u.t_username = username
        u.t_emailaddr = email
        u.t_password = password
        u.t_gender = int(gender)
        db.session.add(u)
        db.session.commit()
        ext = ExtInfo()
        ext.t_uid = u.t_uid
        if u.t_gender:
            ext.t_avatar = '/static/images/avatar_default_boy.png'
        else:
            ext.t_avatar = '/static/images/avatar_default_girl.png'
        db.session.add(ext)
        db.session.commit()
        session['email'] = u.t_emailaddr
        session['username'] = u.t_username
        session['password'] = u.t_password
        return jsonify(username=u.t_username, emailaddr=u.t_emailaddr)
    except KeyError, ex:
        raise APIError(ex.message, 500)


@app.route('/api/auth', methods=['POST'])
def api_authenticate():
    try:
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        try:
            remember = request.form['remember'].strip()
            if isinstance(remember, str):
                if remember == 'on':
                    remember = 1
            else:
                remember = int(remember)
        except KeyError:
            remember = 0
        user = User.query.filter_by(t_emailaddr=email).first()
        if not user:
            raise APIError('User does not exist', 200)
        if not user.t_password == password:
            raise APIError('Wrong password', 200)
        if remember:
            session.permanent = True
        session['email'] = user.t_emailaddr
        session['username'] = user.t_username
        session['password'] = user.t_password
        return jsonify(username=user.t_username, emailaddr=user.t_emailaddr)
    except KeyError, e:
        raise APIError(e.message, 500)


@app.route('/api/user/passwd', methods=['POST'])
def api_change_passwd():
    try:
        prev_password = request.form['prev_passwd'].strip().lower()
        new_password = request.form['new_passwd'].strip().lower()
        captcha = request.form['captcha'].strip().lower()
        cap_answer = session['captcha'].lower()
        if not captcha == cap_answer:
            raise APIError('Wrong captcha!', 200)
        user = get_current_user()
        if not _RE_MD5.match(prev_password) or not _RE_MD5.match(new_password):
            raise APIError('Invalid password format')
        if not user.t_password == prev_password:
            raise APIError('The previous password is wrong.')
        user.t_password = new_password
        db.session.commit()
        cancel_session()
        return jsonify(value='')
    except KeyError, e:
        raise APIError(e.message, 500)
    except AttributeError, ex:
        raise APIError(ex.message, 500)


@app.route('/api/user/<emailaddr>', methods=['GET'])
def api_show_userinfo(emailaddr):
    try:
        u = User.query.filter_by(t_emailaddr=emailaddr).first()
        if not u:
            u = get_current_user()
        u_ext = ExtInfo.query.filter_by(t_uid=u.t_uid).first()
        user_dict = {'uid': u.t_uid, 'username': u.t_username, 'email': u.t_emailaddr,
                     'gender': u.t_gender, 'isadmin': u.t_privilege,
                     'credits': u.t_credits, 'created_at': u.t_created_at,
                     'avatar': u_ext.t_avatar, 'motto': u_ext.t_motto,
                     'qq': u_ext.t_qqid, 'cellphone': u_ext.t_cellphone,
                     'zipcode': u_ext.t_zipcode, 'website': u_ext.t_website,
                     'birthday': u_ext.t_birthday}
        return jsonify(user_dict)
    except KeyError, e:
        raise APIError(e.message, 500)
    except AttributeError, ex:
        raise APIError(ex.message, 500)


@app.route('/api/user/edit', methods=['POST'])
def api_edit_info():
    try:
        user = get_current_user()
        ext = ExtInfo.query.filter_by(t_uid=user.t_uid).first()
        username = request.form['username'].strip()
        gender = request.form['gender'].strip()
        avatar = request.form['avatar'].strip()
        motto = request.form['motto'].strip()
        qq = request.form['qq'].strip()
        cellphone = request.form['cellphone'].strip()
        zipcode = request.form['zipcode'].strip()
        website = request.form['website'].strip()
        birthday = request.form['birthday'].strip()
        user.t_username = username
        user.t_gender = gender
        ext.t_avatar = avatar
        ext.t_motto = motto
        ext.t_qqid = qq
        ext.t_cellphone = cellphone
        ext.t_zipcode = zipcode
        ext.t_website = website
        ext.t_birthday = birthday
        db.session.commit()
        return jsonify(user=user.getDict(), usrext=ext.getDict())
    except Exception:
        print traceback.format_exc()
        raise APIError(traceback.format_exc(), 500)


@app.route('/api/avatar', methods=['POST'])
def api_upload_avatar():
    try:
        img_file = request.form['img']
        content_type, body = process_file(img_file)
        mime, extension = content_type.split('/')
        if not mime == 'image':
            raise APIError('You can only upload an image.')
        user = get_current_user()
        ext = ExtInfo.query.filter_by(t_uid=user.t_uid).first()
        filename_seed = str(time.time())
        filename = hashlib.md5(filename_seed).hexdigest() + '.' + extension
        path = 'static/images/uploads/' + filename
        ext.t_avatar = path
        db.session.commit()
        with open(path, 'wb') as f:
            f.write(body)
        return jsonify(src=path)
    except KeyError:
        print traceback.format_exc()
        raise APIError(traceback.format_exc(), 500)


def process_file(data):
    head, body = data.split(',')
    desc = head.split(':')[1]
    mime, encoding = desc.split(';')
    if encoding == 'base64':
        body = b64decode(body)
    return mime, body


@app.route('/logout', methods=['GET'])
def api_logout():
    cancel_session()
    return redirect(url_for('.index'))


def cancel_session():
    try:
        session.pop('username', None)
        session.pop('email', None)
        session.pop('password', None)
    except:
        pass


# Socket IO apis
@socketio.on('join')
def on_join(data):
    global players
    username = session['username']
    email = session['email']
    room = session['room']
    join_room(room)
    p = Player(username, email, data['user'])
    if players.has_key(room):
        players[room][0].append(p)
    else:
        players[room] = [[], '1', '1']
        players[room][0].append(p)
    emit('msg', username + ' has joined the group' + room, room=room)
    emit('user', p.get_id(), room=room)
    emit('join', room)


@socketio.on('leave')
def on_leave(data):
    global players
    username = session['username']
    email = session['email']
    room = data['room']
    leave_room(room)
    if players.has_key(room):
        for i in range(players[room][0].__len__()):
            print i
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
    ready_to_go = False
    if players.has_key(room):
        ready_to_go = True
        # Set current player ready
        for i in players[room][0]:
            if i.email == email:
                i.ready = True
        # Query for whether all users are ready.
        for i in players[room][0]:
            print i.ready
            if not i.ready == True:
                ready_to_go = False
                break
    if ready_to_go:
        print 'readyok'
        players[room][0][0].is_turn = True
        emit('ready', room=data['room'])
        pick_word(data['room'])
        emit('word', {'user': players[room][0][0].get_id(), 'word': players[room][1]}, room=data['room'])


@socketio.on('draw')
def on_draw(data):
    emit('draw', data['point'], room=data['room'])


@socketio.on('get_word')
def on_get_word(data):
    '''
        Get a word from the database randomly
    '''
    pick_word()
    user = ''
    if players.has_key(session['room']):
        for i in players[session['room']][0]:
            if i.is_turn:
                user = i.get_id()
    emit('word', {'user': user, 'word': players[session['room']][1]}, room=session['room'])
    # emit('draw', data, room=data['room'])


@socketio.on('get_desc')
def on_get_desc(data):
    room = data['room']
    emit('msg', players[room][2], room=data['room'])


@socketio.on('msg')
def on_chat(data):
    global players
    room = data['room']
    # Check if guessed right. If so no display.
    if data['message'] == players[room][1]:
        if players.has_key(room):
            for i in range(players[room][0].__len__()):
                if players[room][0][i].email == session['email']:
                    print 'ok'
                    players[room][0][i].answer_ok()
                    players[room][0][i].add_points(3)
                    emit('user_answer_ok', players[room][0][i].get_id(), room=room)
            try:
                pick_word(room)
                for i in range(players[room][0].__len__()):
                    if players[room][0][i].is_turn:
                        players[room][0][i].is_turn = False
                        players[room][0][i+1].is_turn = True
                        break
                for i in range(players[room][0].__len__()):
                    if players[room][0][i].is_turn:
                        emit('word', {'user': players[room][0][i].get_id(), 'word': players[room][1]}, room=data['room'])
                        break
            except IndexError:
                print('IndexError')
                emit('end_this_session', '', room=room)
            # Check: If all players have correctly answerd, the game ends.
            flag_end = True
            for i in players[room][0]:
                if not i.answer:
                    flag_end = False
                    break
            if flag_end:
                print('Flag-end = 1')
                emit('end_this_session', room, room=room)
    else:
        emit('msg', session['username'] + ':' + data['message'],
             json=False, room=data['room'])


@socketio.on('clear')
def clear(data):
    emit('clear', {}, room=data['room'])


@socketio.on('end')
def on_game_end(data):
    # Check out all players
    if isinstance(players[data['room']][0], list):
        for i in players[data['room']][0]:
            check_out_player(i)
    return players.pop(data['room'])


def pick_word(room):
    global players
    rows = Word.query.count()
    num = randrange(rows)
    word = Word.query.filter_by(t_id=num+1).first()
    players[room][1] = word.t_word
    players[room][2] = word.t_desc


def check_out_player(player):
    '''
        Check out a player
    '''
    # Get corresponding user object
    user = User.query.filter_by(t_emailaddr=player.email).first()
    player.ready = False
    user.t_credits += player.get_points()
    db.session.commit()

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
    app.jinja_env.filters['datetime'] = datetime_filter
    socketio.run(app, host='0.0.0.0')
