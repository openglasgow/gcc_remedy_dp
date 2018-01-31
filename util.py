from __future__ import absolute_import
import logging 
from orm.orm import db_connect, create_tables, Base
from orm.models import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone, time
import subprocess

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


def batch_dates(start_date = "09-01-2017", end_date= "09-01-2017", batch_size=3):
    '''
    Neatly splits up date ranges into a list of tuples representing
    start and end time for each batch range, truncates at the end if its not even. 
    '''
    ### set up vars
    start_date = datetime.strptime(start_date, "%m-%d-%Y")
    end_date = datetime.strptime(end_date, "%m-%d-%Y")
    difftime_days = (end_date - start_date).days
    days_remainder = difftime_days % batch_size
    ### if the start and end dates are smaller than batch size, just return start and end dates
    if difftime_days <= batch_size:
        dates_list = [(start_date.strftime("%m-%d-%Y"), end_date.strftime("%m-%d-%Y"))]
        return(dates_list)
    ### Otherwise build a list with a sequence of dates 
    diffdates_list = [batch_size for i in range(0, int((difftime_days-days_remainder)/batch_size))]
    dates_list = [((start_date + timedelta(days = i*diffdates_list[i])).strftime("%m-%d-%Y"), (start_date + timedelta(days = i*diffdates_list[i]+batch_size)).strftime("%m-%d-%Y")) for i in range(0, len(diffdates_list))]
    #add a remainder if there is one
    if days_remainder > 0:
        dates_list.append((dates_list[-1][1], (datetime.strptime(dates_list[-1][1], "%m-%d-%Y") + timedelta(days = days_remainder)).strftime("%m-%d-%Y")))

    return(dates_list)


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

def get_model_obj(api, row):
    '''
    Takes user supplied string output and returns SQLa
    model object
    '''
    if api == "live":
        obj = LiveCase(**row)
    elif api == "archive":
        obj = ArchiveCase(**row)
    elif api == "complaints":
        obj = ComplaintCase(**row)
    elif api == "test":
        obj = RemedyCase(**row)
    elif api == "remedy":
        obj = RemedyCase(**row)
    return(obj)

## Open / Close tunnel
def tunnel(command):
    return(subprocess.call(['./tunnel', '{}'.format(command)]))


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