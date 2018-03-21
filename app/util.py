from __future__ import absolute_import
import logging 
from orm.orm import db_connect, create_tables, Base
from time import sleep
from orm.models import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone, time
import subprocess
from dateutil.parser import parser
from .errors import ConnectionError
from config.settings import fetch_date_format

def gen_session(connection):
    '''
    Creates new SQLa session, see orm.orm for more info. 
    '''
    engine = db_connect(connection)
    create_tables(engine, Base)
    Session = sessionmaker(bind=engine)
    session = Session()
    return(session)

def setup_logger(logger_name, log_file, level=logging.INFO):
    '''
    Set up loggers that outputs to file and stdout
    '''
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s -- %(levelname)s: %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)


def parse_dates(row, field_list, parse_string = "%Y-%m-%dT%H:%M:%S.%f"):
    '''
    Takes raw date input from API responses and 
    parses them into datetime objects
    '''
    for field in field_list:
        try:
            row[field] = datetime.strptime(row[field], parse_string)
        except:
            row[field] = None
    return(row)

def get_model_obj(table, row={}):
    '''
    Takes user supplied string output and returns SQLa
    model class or instance if row data is present
    '''
    if table == "archive":
        obj = ArchiveCase
    elif table == "remedy":
        obj = RemedyCase
    elif table == "remedy_test":
        obj = RemedyTest
    elif table == "archive_test":
        obj = ArchiveTest
    # if row data
    if row:
        obj = obj(**row)

    return(obj)

## Open / Close tunnel
def tunnel(command):
    command = './tunnel {}'.format(command)
    return(subprocess.run(command.split()).returncode)

def tunnel_open():
    command = 'nc -z localhost 5556'
    return(True if subprocess.run(command.split()).returncode == 0 else False)

def tunnel_db_connect(timeout = 10):
  ''' Opens the tunnel, waits until a db connection can be made
  then returns the session when it does
  '''
  tunnel('open')
  while not tunnel_open():
    sleep(2)
  db_connection = None
  timeout_counter = 0
  while db_connection is None:
    try: 
      rs = gen_session('remote')
      db_connection = rs.connection()
    except:
      sleep(1)
      timeout_counter += 1
      if timeout_counter >= timeout:
        raise ConnectionError("Connection attempt timed out")
      else:
        pass
  return(rs)

## Set up metadata
md = Base.metadata

def write_schema(md):
    ''' 
    Writes out DB schema's to file
    '''
    with open('../schema.txt', 'w') as f:
        f.write("*** WB Schema at {0} \n------------------------\n\n".format(datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")))
        for table in md.sorted_tables:
            f.write("{0}:\n".format(table))
            for column in table.c:
                fk = ", {0}".format(list(column.foreign_keys)[0]) if len(column.foreign_keys) > 0 else ""
                pk = ", primary_key" if column.primary_key == True else ""
                f.write("\t{0}, :{1}{2}{3}\n".format(column.name, column.type,fk,pk))