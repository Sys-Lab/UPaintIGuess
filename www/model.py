__author__ = 'Excelle'

from sqlalchemy import String, Integer, Float, Column
from db import Base
import time


class User(Base):
    __tablename__ = 'a_usrs'
    t_uid = Column(Integer, primary_key=True, autoincrement=True)
    t_username = Column(String(32), nullable=False)
    t_password = Column(String(32), nullable=False)
    t_emailaddr = Column(String(128), nullable=False)
    t_gender = Column(Integer)
    t_privilege = Column(Integer, default=0)
    t_credits = Column(Integer, default=10)
    t_created_at = Column(Float, default=time.time())


class ExtInfo(Base):
    __tablename__ = 'a_usrext'
    t_uid = Column(Integer, primary_key=True, autoincrement=True)
    t_avatar = Column(String)
    t_motto = Column(String(80))
    t_qqid = Column(String(12))
    t_cellphone = Column(String(11))
    t_zipcode = Column(String(6))
    t_website = Column(String)
    t_birthday = Column(Float)


class Word(Base):
    __tablename__ = 'a_words'
    t_id = Column(Integer, primary_key=True, autoincrement=True)
    t_word = Column(String(16))
    t_desc = Column(String(24))
