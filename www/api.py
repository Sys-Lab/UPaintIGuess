import json
import time
import hashlib
from datetime import datetime


class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=200, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.status_code
        rv['data'] = ''
        rv['message'] = self.message
        return rv


class Player(object):
    username = ''
    email = ''
    ready = False
    answer = False
    is_turn = False
    points = 0
    user_id = ''

    def __init__(self, username, email, key):
        super(Player, self).__init__()
        self.username = username
        self.email = email
        self.user_id = key
        print(username + ':' + email + ':' + self.user_id)

    def ready(self):
        self.ready = True

    def is_ready(self):
        return self.ready

    def answer_ok(self):
        self.answer = True
        self.is_turn = False

    def get_points(self):
        return self.points

    def add_points(self, x):
        self.points += x

    def set_is_turn(self, x):
        self.is_turn = False

    def get_id(self):
        return self.user_id


def dump_class(cls):
    return json.dumps(cls, default=lambda obj: obj.__dict__)


def datetime_filter(t):
    if not t:
        t = 0;
    delta = int(time.time() - t)
    if delta < 60:
        return u'1 minute ago'
    if delta < 3600:
        return u'%s minutes ago' % (delta // 60)
    if delta < 86400:
        return u'%s hours ago' % (delta // 3600)
    if delta < 604800:
        return u'%s days ago' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s/%s/%s' % (dt.year, dt.month, dt.day)
