from flask.ext.sqlalchemy import SQLAlchemy
from time import time

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    uid = db.Column('uid', db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column('phonenum', db.String(32), nullable=False)
    password = db.Column('password', db.String(32), nullable=False)
    permission = db.Column('permission', db.Integer, nullable=False)
    online = db.Column('online', db.Integer, nullable=True)
    created_at = db.Column('created_at', db.Float, nullable=False)
    last_login = db.Cookie('last_login', db.Float, nullable=False)


class UserSchool(db.Model):
    __tablename__ = 'user_school'
    uid = db.Column('uid', db.Integer, primary_key=True, nullable=False)
    school_name = db.Column('school_name', db.Text)
    degree = db.Column('degree', db.Integer)
    school_id = db.Column('school_id', db.Integer)
    school_province = db.Column('school_province', db.Integer)
    school_city = db.Column('school_city', db.Integer)
    auth_photo = db.Column('auth_photo', db.Text)
    auth_pass = db.Column('pass', db.Boolean)


class UserMeta(db.Model):
    __tablename__ = 'user_meta'
    uid = db.Column('uid', db.Integer, primary_key=True, nullable=False)
    nickname = db.Column('nickname', db.String(32))
    realname = db.Column('realname', db.String(32))
    gender = db.Column('gender', db.Integer)
    age = db.Column('age', db.Integer)
    height = db.Column('height', db.Float)
    birthday = db.Column('birthday', db.Float)
    horoscope = db.Column('horoscope', db.Integer)
    hometown_province = db.Column('hometown_province', db.Integer)
    hometown_city = db.Column('hometown_city', db.Integer)
    hometown_addr = db.Column('hometown_addr', db.Text)
    workplace_province = db.Column('workplace_province', db.Integer)
    workplace_city = db.Column('workplace_city', db.Integer)
    workplace_addr = db.Column('workplace_addr', db.Text)
    contact = db.Column('contact', db.Text)
    motto = db.Column('motto', db.Text)
    show_contact = db.Column('show_contact', db.Boolean)
    show_name = db.Column('show_name', db.Boolean)


class UserExt(db.Model):
    __tablename__ = 'user_ext'
    uid = db.Column('uid', db.Integer, primary_key=True, nullable=False)
    content = db.Column('content', db.Text)


class Wall(db.Model):
    __tablename__ = 'wall'
    uid = db.Column('uid', db.Integer, primary_key=True, nullable=False)
    photos = db.Column('photos', db.Text)
    upvotes = db.Column('upvotes', db.Integer)
    wall_filter = db.Column('filter', db.Text)


class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    url = db.Column('url', db.Text)
    desc = db.Column('desc', db.Text)
    created_at = db.Column('created_at', db.Float)


class Tweet(db.Model):
    __tablename__ = 'tweets'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    content = db.Column('content', db.Text)
    visibility = db.Column('visibility', db.Integer)
    created_at = db.Column('created_at', db.Float)


class Reply(db.Model):
    __tablename__ = 'replies'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    target = db.Column('target', db.Integer, nullable=False)
    content = db.Column('content', db.Text)
    visibility = db.Column('visibility', db.Integer)
    created_at = db.Column('created_at', db.Float)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    target = db.Column('target', db.Integer, nullable=False)
    content = db.Column('content', db.Text)
    visibility = db.Column('visibility', db.Integer)
    created_at = db.Column('created_at', db.Float)


class Friend(db.Model):
    __tablename__ = 'friends'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    to = db.Column('to', db.Integer, nullable=False)
    group = db.Column('group', db.Integer)
    agree = db.Column('agree', db.Integer)


class FriendGroup(db.Model):
    __tablename__ = 'friend_group'
    user = db.Column('user', db.Integer, primary_key=True)
    content = db.Column('content', db.Text)


class BlackList(db.Model):
    __tablename__ = 'black_list'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    to = db.Column('to', db.Integer, nullable=False)


class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    from = db.Column('from', db.Integer, nullable=False)
    to = db.Column('to', db.Integer, nullable=False)
    content = db.Column('content', db.Text)
    created_at = db.Column('created_at', db.Float)


class AbuseReport(db.Model):
    __tablename__ = 'abuse_report'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    from = db.Column('from', db.Integer, nullable=False)
    target = db.Column('target', db.Integer, nullable=False)
    content = db.Column('content', db.Text)
    created_at = db.Column('created_at', db.Float)


class License(db.Model):
    __tablename__ = 'license'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    content = db.Column('content', db.Text)


class Horoscope(db.Model):
    __tablename__ = 'horoscope'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.Text)
    desc = db.Column('desc', db.Text)


class Province(db.Model):
    __tablename__ = 'province'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.Text)


class City(db.Model):
    __tablename__ = 'city'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    province = db.Column('province', db.Integer, nullable=False)
    name = db.Column('name', db.Text)


class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.Text)
