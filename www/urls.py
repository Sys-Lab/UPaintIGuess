from flask import Flask
from flask import jsonify, session, request
from flask import render_template, make_response
from api import APIError, datetime_filter
from captcha import generate_captcha
from config.config import configs
from model import db

app = Flask(__name__)
db.init_app(app)


@app.route('/')
def index():
    return "Hello World"


def get_mysql_conn_str():
    db_user = configs.db.user
    db_pass = configs.db.password
    db_name = configs.db.database
    db_host = configs.db.host
    db_port = configs.db.port

    return 'mysql+mysqlconnector://' + db_user + ':' + db_pass + '@' + db_host + ':' + str(db_port) + '/' + db_name


if __name__=='__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = get_mysql_conn_str()
    app.config.from_object('config.config')
    app.jinja_env.filters['datetime'] = datetime_filter
    app.run(debug=True)
