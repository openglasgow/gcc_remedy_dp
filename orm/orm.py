## imports
import os
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from orm import settings
from orm.models import *

def db_connect():
    """
    Connects to the database
    """
    return create_engine(os.environ['POSTGRES_URL'], echo=settings.ECHO, client_encoding='utf8')

def create_tables(engine, base):
    """
    Creates or maps the tables in the database
    """
    base.metadata.create_all(engine)

def create_session(base):
    """
    Returns a queryable session
    """
    engine = db_connect()
    create_tables(engine, base)
    Session = sessionmaker(bind=engine)
    return(Session())

