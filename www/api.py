__author__ = 'Excelle'
import json


class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class Player(object):
    username = ''
    email = ''
    ready = False
    answer = False
    points = 0

    def __init__(self, username, email):
        super(Player, self).__init__()
        self.username = username

    def ready(self):
        self.ready = True

    def is_ready(self):
        return self.ready

    def answer_ok(self):
        self.answer = True

    def get_points(self):
        return self.points

    def add_points(self, x):
        self.points += x


def dump_class(cls):
    return json.dumps(cls, default=lambda obj: obj.__dict__)
