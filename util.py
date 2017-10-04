from __future__ import absolute_import
import logging 
from orm.orm import db_connect, create_tables, Base
from orm.models import *
from sqlalchemy.orm import sessionmaker

def gen_session(connection):
    engine = db_connect(connection)
    create_tables(engine, Base)
    Session = sessionmaker(bind=engine)
    session = Session()
    return(session)

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s -- %(levelname)s: %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)


