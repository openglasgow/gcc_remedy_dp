from datetime import datetime, timedelta, timezone, time
from time import sleep
import logging
import sys
from .fetcher import BoFetcher
from config.settings import api_settings, connections, fetch_date_format, parse_date_format
from .util import Util
from .fetcher import BoFetcher

### logging config
Util().setup_logger('crawl_logger', 'logs/crawl.log', logging.DEBUG)
### Setup path

class BoCrawler(object):
    
    def __init__(self, api, connection, model, start_datetime, end_datetime):
        self.api = api
        self.start_datetime = Util().validate_date('fetch', start_datetime)
        self.end_datetime = Util().validate_date('fetch', end_datetime)
        self.connection = connection
        self.model = model
        self.util = Util()
        if connection == "remote":
            self.session = self.util.tunnel_db_connect()
        else:
            self.session = self.set_session(connection)
        self.logger = logging.getLogger('crawl_logger')
        self.batch_size=2

    def set_session(self, connection):
        self.session = self.util.gen_session(connection)
        return(self.session)

    def close_session(self):
        if self.session:
            self.session.close()
            self.session = None
        return(True)

    def get_batch_delta(self):
          '''
            Get last record date in the database and set current date as time we want the record for
          '''
          # Query
          date_field = getattr(self.model, api_settings[self.api]['date_scope_field'])
          last_record_date = self.session.query(date_field).order_by(date_field.desc()).first()[0]
          time_now = datetime.now()
          rs.close()
          batch_delta = self.util.batch_dates(last_record_date.strftime(fetch_date_format), time_now.strftime(fetch_date_format))
          return(batch_delta)

    def crawl(self):
        # Get batched dates from list
        dates_list = self.util.batch_dates(self.start_datetime, self.end_datetime)
        for date_range in dates_list:
            # TODO logging
            self.logger.info("fetching date range {}".format(date_range))
            fetcher = BoFetcher(self.api, date_range[0], date_range[1])
            # Request
            try:
                fetcher.send_request()
                response = fetcher.response
                self.logger.info("Fetched data from {} api with url {} from {} to {} with {} records returned"
                    .format(response["meta"]['api'], response["meta"]['url'],response["meta"]['from_datetime'],response["meta"]['to_datetime'],response["meta"]['length']))
            except:
                e = sys.exc_info()[0]
                raise(e, "Something went wrong fetching data")
            
            if fetcher.response == b'':
                #log it as no response
                
                pass
            # To DB
            try:
                self.response_to_db(response)
                self.logger.info("saved {} records to db".format(len(response['data'])))
            except:
                pass

    def response_to_db(self, response):
        '''
        Save api response to database
        '''
        rows = response["data"]
        try:
            for id,row in rows.items():
                row = self.util.parse_dates(row, api_settings[self.api]['date_fields'])
                row_id = api_settings[self.api]['row_id'].lower()
                # Get the object if it exists in the DB, or create a new one
                # TODO check for certain fields being updated 
                obj = get_or_create(self.session, self.model, **{row_id: id})
                ### Todo log if created or updated
                obj = self.session.query(model).filter(model.id == obj.id).update(row)
            self.session.commit(  )
            # result = (True, "%s cases written to the database"%(parsed_response["meta"]["length"]))
        except:
            e = sys.exc_info()[0]
            result = (False, str(e) + "Thrown from response_to_db")
        finally:
            self.session.close()
            return(result)


# def api_extractor(api="live", batch_size=3, sleep_time = 3,  start_date = "01-01-2017 00:00:00 AM", end_date="01-02-2017 00:00:00 AM", connection="local"):
#     extraction_logger.info("*** Batch extraction starting with batch size of %s, sleep time of %s, from %s to %s." %(batch_size, sleep_time, start_date, end_date))
#     ### Generate a tuple of date ranges, then for each one
#     dates_list = batch_dates(start_date, end_date, batch_size)
#     ### iterate through the batch dates and put the results in the db
#     for date_range in dates_list:
#         extraction_logger.info("Polling %s to %s" % (date_range[0], date_range[1]))
#         ### poll the current date range for cases
#         try:
#             response = poll_api(api, date_range[0], date_range[1])
#             extraction_logger.info("Successfully polled api from %s to %s with %s results"%(date_range[0], date_range[1], response["meta"]["length"]))
#         except:
#             extraction_logger.error(str(sys.exc_info()[0]) + "Thrown from api_extractor")
#             ### skip to next iteration
#             continue
#         ### if the api read worked send them to db
#         db_result = response_to_db(api, response, connection)
#         if db_result[0]:
#             ### Everything went ok
#             extraction_logger.info(db_result[1])
#         else:
#             ### There was an error
#             extraction_logger.error(db_result[1] + "thrown from api_extractor")
#         extraction_logger.debug("sleeping for %s seconds" % (sleep_time))
#         sleep(sleep_time)
#     extraction_logger.info("*** Batch extraction for %s to %s complete ***" % (start_date, end_date))
#     return(True)

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
