from datetime import datetime, timedelta, timezone, time
from time import sleep
import logging
import sys
from .fetcher import BoFetcher
from config.settings import api_settings, connections, fetch_date_format
from .util import gen_session, setup_logger

### logging config
setup_logger('extraction_logger', 'logs/extraction.log', logging.DEBUG)
extraction_logger = logging.getLogger('extraction_logger')
### Setup path

class BoCrawler(object):
    
    def __init__(self, api, connection, model, start_datetime, end_datetime):
        self.api = api
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.connection = connection
        self.model = model
        self.session = self.set_session(connection)

    def set_session(self, connection):
        self.session = gen_session(connection)
        return(self.session)

    def close_session(self):
        if self.session:
            self.session.close()
            self.session = None
        return(True)

    def batch_dates(self, batch_size=2, fetch_date_format=fetch_date_format):
        '''
        Neatly splits up date ranges into a list of tuples representing
        start and end time for each batch range, truncates at the end if its not even. 
        '''
        start_time = self.start_datetime
        end_time = self.end_datetime

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

            

def response_to_db(api, parsed_response, connection='local'):
    ## Setup session
    session = gen_session(connection)
    ## place data in session
    rows = parsed_response["data"]
    try:
        for id,row in rows.items():
            row = parse_dates(row, settings[api]['date_fields'])
            model_obj = get_model_obj(api, row)
            session.add(model_obj)
        session.commit(  )
        result = (True, "%s cases written to the database"%(parsed_response["meta"]["length"]))
    except:
        e = sys.exc_info()[0]
        result = (False, str(e) + "Thrown from response_to_db")
    finally:
        session.close()
        return(result)


def api_extractor(api="live", batch_size=3, sleep_time = 3,  start_date = "01-01-2017 00:00:00 AM", end_date="01-02-2017 00:00:00 AM", connection="local"):
    extraction_logger.info("*** Batch extraction starting with batch size of %s, sleep time of %s, from %s to %s." %(batch_size, sleep_time, start_date, end_date))
    ### Generate a tuple of date ranges, then for each one
    dates_list = batch_dates(start_date, end_date, batch_size)
    ### iterate through the batch dates and put the results in the db
    for date_range in dates_list:
        extraction_logger.info("Polling %s to %s" % (date_range[0], date_range[1]))
        ### poll the current date range for cases
        try:
            response = poll_api(api, date_range[0], date_range[1])
            extraction_logger.info("Successfully polled api from %s to %s with %s results"%(date_range[0], date_range[1], response["meta"]["length"]))
        except:
            extraction_logger.error(str(sys.exc_info()[0]) + "Thrown from api_extractor")
            ### skip to next iteration
            continue
        ### if the api read worked send them to db
        db_result = response_to_db(api, response, connection)
        if db_result[0]:
            ### Everything went ok
            extraction_logger.info(db_result[1])
        else:
            ### There was an error
            extraction_logger.error(db_result[1] + "thrown from api_extractor")
        extraction_logger.debug("sleeping for %s seconds" % (sleep_time))
        sleep(sleep_time)
    extraction_logger.info("*** Batch extraction for %s to %s complete ***" % (start_date, end_date))
    return(True)

# if __name__ == "__main__":
#     ### Set up cli arguments
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-a", "-api", dest="api", default="live", required=True, help="select api from live, complaints or archive")
#     parser.add_argument("-sd", "--startdate", dest="startdate", default="09-01-2017", help="format m/d/y ie 09-01-2017", required=True)
#     parser.add_argument("-ed", "--enddate", dest="enddate", default="09-03-2017", help="format m/d/y ie 09-01-2017", required=True)
#     parser.add_argument("-s", "--sleep", dest="sleep", default=3, type=int, help="amount of seconds you want between api requests")
#     parser.add_argument("-b", "--batchsize", dest="batchsize", default=5, type=int, help="days interval between start and end dates to batch api requests")
#     parser.add_argument("-c", "--connection", dest="connection", default='local', type=str, help="The connection to draw from the orm settings")
#     args = parser.parse_args()
#     print("extracting remedy cases from %s to %s, this may take a while..." % (args.startdate, args.enddate))
#     api_extractor(args.api, args.batchsize, args.sleep, args.startdate, args.enddate, args.connection)
#     print("All done!") 
