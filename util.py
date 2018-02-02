from __future__ import absolute_import
import logging 
from orm.orm import db_connect, create_tables, Base
from orm.models import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone, time
import subprocess
from dateutil.parser import parser

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


def batch_dates(start_time = "09-01-2017 00:00:00 AM", end_time= "09-01-2017 00:00:00 AM", batch_size=2):
    '''
    Neatly splits up date ranges into a list of tuples representing
    start and end time for each batch range, truncates at the end if its not even. 
    '''
    ### Set up necessary vars for top tail
    start_datetime = datetime.strptime(start_time, "%m-%d-%Y %H:%M:%S %p")
    end_datetime = datetime.strptime(end_time, "%m-%d-%Y %H:%M:%S %p")

    top_next = beginning_of_day(start_datetime + timedelta(days=1)).strftime("%m-%d-%Y %H:%M:%S %p")
    top = (start_time, top_next)
    
    tail_first = beginning_of_day(end_datetime).strftime("%m-%d-%Y %H:%M:%S %p")
    tail = (tail_first, end_time)

    # If its within the same day
    if top_next > tail_first:
        return([(start_time, end_time)])

    # If the difference is less than 24 hours
    if (end_datetime - start_datetime).total_seconds() // 3600 <= 24:
        if tail[0] == tail[1]:
            return([top])
        else:
            return([top, tail])

    ### set up vars
    start_date = datetime.strptime(top_next, "%m-%d-%Y %H:%M:%S %p")
    end_date = datetime.strptime(tail_first, "%m-%d-%Y %H:%M:%S %p")
    

    difftime_days = (end_date - start_date).days
    days_remainder = difftime_days % batch_size

    ### if the start and end dates are smaller than batch size, just return start and end dates
    if difftime_days <= batch_size:
        dates_list = [(start_date.strftime("%m-%d-%Y %H:%M:%S %p"), end_date.strftime("%m-%d-%Y %H:%M:%S %p"))]
        if tail[0] == tail[1]:
            return([top]+dates_list)
        else:
            return([top]+dates_list+[tail])
    
    ### Otherwise build a list with a sequence of dates 
    diffdates_list = [batch_size for i in range(0, int((difftime_days-days_remainder)/batch_size))]
    dates_list = [((start_date + timedelta(days = i*diffdates_list[i])).strftime("%m-%d-%Y %H:%M:%S %p"), (start_date + timedelta(days = i*diffdates_list[i]+batch_size)).strftime("%m-%d-%Y %H:%M:%S %p")) for i in range(0, len(diffdates_list))]
    #add a remainder if there is one
    if days_remainder > 0:
        dates_list.append((dates_list[-1][1], (datetime.strptime(dates_list[-1][1], "%m-%d-%Y %H:%M:%S %p") + timedelta(days = days_remainder)).strftime("%m-%d-%Y %H:%M:%S %p")))

    if tail[0] == tail[1]:
        return([top]+dates_list)
    else:
        return([top]+dates_list+[tail])

def beginning_of_day(date_obj):
    return(datetime.combine(date_obj, time()))

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