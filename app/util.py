import os
import logging 
import sys
from orm.orm import db_connect, create_tables, Base
from time import sleep
from orm.models import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone, time
import subprocess
from dateutil.parser import parser
from .errors import ConnectionError
from config.settings import fetch_date_format, parse_date_format
import psycopg2

class Util(object):
    def __init__(self):
        pass

        
    def validate_date(self, format, date):
        '''
        Validates date based on fetch or parse format
        '''
        if format == "fetch":
            try: 
                datetime.strptime(date, fetch_date_format)
                return(date)
            except ValueError:
                raise ValueError("Date {} not formatted correctly, use the format \"{}\"".format(date, fetch_date_format))
        elif format=="parse":
            try: 
                datetime.strptime(date, parse_date_format)
                return(date)
            except ValueError:
                raise ValueError("Date {} not formatted correctly, use the format \"{}\"".format(date, parse_date_format))



    def batch_dates(self, start_datetime, end_datetime, batch_size=2, fetch_date_format=fetch_date_format):
            '''
            Neatly splits up date ranges into a list of tuples representing
            start and end time for each batch range, truncates at the end if its not even. 
            '''
            start_time = start_datetime
            end_time = end_datetime

            ### Set up necessary vars for top tail
            start_datetime = datetime.strptime(start_time, fetch_date_format)
            end_datetime = datetime.strptime(end_time, fetch_date_format)

            top_next = self.beginning_of_day(start_datetime + timedelta(days=1)).strftime(fetch_date_format)
            top = (start_time, top_next)
            
            tail_first = self.beginning_of_day(end_datetime).strftime(fetch_date_format)
            tail = (tail_first, end_time)

            # If its within the same day
            if datetime.strptime(top_next, fetch_date_format) >  datetime.strptime(tail_first, fetch_date_format):
                return([(start_time, end_time)])

            # If the difference is less than 24 hours
            if (end_datetime - start_datetime).total_seconds() // 3600 <= 24:
                if tail[0] == tail[1]:
                    return([top])
                else:
                    return([top, tail])

            ### set up vars
            start_date = datetime.strptime(top_next, fetch_date_format)
            end_date = datetime.strptime(tail_first, fetch_date_format)
            

            difftime_days = (end_date - start_date).days
            days_remainder = difftime_days % batch_size

            ### if the start and end dates are smaller than batch size, just return start and end dates
            if difftime_days <= batch_size:
                dates_list = [(start_date.strftime(fetch_date_format), end_date.strftime(fetch_date_format))]
                if tail[0] == tail[1]:
                    return([top]+dates_list)
                else:
                    return([top]+dates_list+[tail])
            
            ### Otherwise build a list with a sequence of dates 
            diffdates_list = [batch_size for i in range(0, int((difftime_days-days_remainder)/batch_size))]
            dates_list = [((start_date + timedelta(days = i*diffdates_list[i])).strftime(fetch_date_format), (start_date + timedelta(days = i*diffdates_list[i]+batch_size)).strftime(fetch_date_format)) for i in range(0, len(diffdates_list))]
            
            #add a remainder if there is one
            if days_remainder > 0:
                dates_list.append((dates_list[-1][1], (datetime.strptime(dates_list[-1][1], fetch_date_format) + timedelta(days = days_remainder)).strftime(fetch_date_format)))

            # Final return
            if tail[0] == tail[1]:
                return([top]+dates_list)
            else:
                return([top]+dates_list+[tail])

    def beginning_of_day(self, date_obj):
        return(datetime.combine(date_obj, time()))

    def gen_session(self, connection):
        '''
        Creates new SQLa session, see orm.orm for more info. 
        '''
        engine = db_connect(connection)
        create_tables(engine, Base)
        Session = sessionmaker(bind=engine)
        session = Session()
        return(session)

    def setup_logger(self, logger_name, log_file, level=logging.INFO):
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


    def parse_dates(self, row, field_list, parse_string=parse_date_format):
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

    def get_model_obj(self, table, row={}):
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
    def tunnel(self, command):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print(dir_path)
        command = '{}/tunnel {}'.format(dir_path,command)
        return(subprocess.run(command.split()).returncode)

    def tunnel_open(self):
        command = 'nc -z localhost 5556'
        return(True if subprocess.run(command.split()).returncode == 0 else False)

    def tunnel_db_connect(self, timeout = 10):
      ''' Opens the tunnel, waits until a db connection can be made
      then returns the session when it does
      '''
      self.tunnel('open')
      while not self.tunnel_open():
        sleep(2)
      db_connection = None
      timeout_counter = 0
      while db_connection is None:
        try: 
          rs = self.gen_session('remote')
          db_connection = rs.connection()
        except:
          return(e)
          sleep(1)
          timeout_counter += 1
          if timeout_counter >= timeout:
            raise ConnectionError("Connection attempt timed out, check you have a password in the env")
          else:
            pass
      return(rs)

    ## Set up metadata
    md = Base.metadata

    def write_schema(self, md):
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