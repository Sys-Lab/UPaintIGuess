__author__ = 'Excelle'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from config import config

db_user = config.configs.db.user
db_pass = config.configs.db.password
db_name = config.configs.db.database
db_host = config.configs.db.host
db_port = config.configs.db.port

engine = create_engine('mysql+mysqlconnector://' + db_user + ':' + db_pass + '@' + db_host + ':' +
                       db_port + '/' + db_name)

db_session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # Import all needed modules which define data models so that
    # they will be registered to the metadata.
    import model
    Base.metadata.create_all(bind=engine)