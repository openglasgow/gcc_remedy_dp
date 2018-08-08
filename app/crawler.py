from datetime import datetime, timedelta, timezone, time
from time import sleep
import logging
import sys
import re
from .fetcher import BoFetcher
from config.settings import api_settings, connections, fetch_date_format, parse_date_format, crawl_delay
from .util import Util
from .fetcher import BoFetcher

### logging config
Util().setup_logger('crawl_logger', 'logs/crawl.log', logging.DEBUG)
### Setup path

class BoCrawler(object):
    
    def __init__(self, api, connection, model, start_datetime=None, end_datetime=None, delta=False):
        self.api = api
        self.connection = connection
        self.model = model
        self.delay = crawl_delay
        self.util = Util()
        if connection == "remote":
            self.session = self.util.tunnel_db_connect()
        else:
            self.session = self.set_session(connection)
        self.logger = logging.getLogger('crawl_logger')
        self.batch_size=2
        ### If start and end are supplied, set the instance variables
        if start_datetime and end_datetime:
            start_datetime = self.util.validate_date('fetch', start_datetime)
            end_datetime = self.util.validate_date('fetch', end_datetime)
            self.batch_list = self.util.batch_dates(start_datetime, end_datetime)
        ### If its a batch query, set 
        if delta:
            self.batch_list = self.get_batch_delta()

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
          batch_delta = self.util.batch_dates(last_record_date.strftime(fetch_date_format), time_now.strftime(fetch_date_format))
          return(batch_delta)

    def crawl(self):
        # Get batched dates from list
        dates_list = self.batch_list
        # info
        self.logger.info("Starting crawl from {} to {}".format(dates_list[0][0], dates_list[-1][1]))
        for date_range in dates_list:
            # TODO logging
            self.logger.info("fetching date range {}".format(date_range))
            fetcher = BoFetcher(self.api, date_range[0], date_range[1])
            # Request
            try:
                fetcher.send_request()
                response = fetcher.response
                self.logger.info("Fetched data from {} api from {} to {} with {} records returned"
                    .format(response["meta"]['api'], response["meta"]['from_datetime'], response["meta"]['to_datetime'], response["meta"]['length']))
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
                e = sys.exc_info()[0]
                raise(e)
            # Pause before the next iteration
            self.logger.info("pausing for {} seconds".format(self.delay))
            sleep(self.delay)
        self.logger.info("All Done!")

    def response_to_db(self, response):
        '''
        Save api response to database
        '''
        rows = response["data"]
        try:
            row_objects = {id: self.model(**row) for id, row in rows.items()}

            for record in self.session.query(self.model).filter(self.model.call_id.in_(row_objects.keys())).distinct(self.model.call_id).all():
                # Only merge those posts which already exist in the database
                if record is None:
                    continue
                try: 
                    self.session.merge(row_objects.pop(record.call_id))
                except KeyError:
                    self.logger.error("record {} may be duplicated, continuing to next item".format(record))
                    continue
            # Log updates
            self.logger.debug("{} existing records updated".format(len(rows) - len(row_objects)))
            # Add the rest
            self.session.add_all(row_objects.values())
            self.session.commit()
            # Log the new records
            self.logger.debug("{} new records added".format(len(row_objects)))
        except:
            e = sys.exc_info()[0]
            raise(e)
        finally:
            self.session.close()

    def set_range(self, period):
        '''
        little DSL to parse time deltas and set date range to crawl
        '''
        if not re.match(r'\d+\D', period):
            raise ValueError(
                '''Query must be two elements, the first being an integer describing the length of delta, 
                    and the second a character describing the unit of time. \n
                    accepted formats: mins, hours, days, weeks, months, years''')
        ### parse
        n = int(re.search(r'\d+', period)[0])
        unit = re.search(r'\D+', period)[0]
        ### Set up deltas
        if unit == 'mins':
            delta = timedelta(minutes = n)
        if unit == 'hour':
            delta = timedelta(hours = n)
        if unit == 'days': 
            delta = timedelta(days = n)
        if unit == 'weeks': 
            delta = timedelta(days = n * 7)
        if unit == 'months': 
            delta = timedelta(days = n*365/12)
        if unit == 'years':
            delta = timedelta(days = n*365)

        # Set to instance and return list
        self.batch_list = self.util.batch_dates(datetime.strftime(datetime.now() - delta, fetch_date_format), datetime.strftime(datetime.now(), fetch_date_format))
        return self.batch_list
