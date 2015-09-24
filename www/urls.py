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

app = Flask(__name__)
socketio = SocketIO(app)
players = dict()
db = SQLAlchemy(app)


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
