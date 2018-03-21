from datetime import datetime, timedelta, timezone, time
from time import sleep
from app.poll_api import get_wsdl_payload, config_wsdl_payload, send_request, parse_xml 
import logging
import argparse
import sys
from config.api_settings import settings, date_format
import importlib
from app.util import *
from app.pi_to_db import poll_api, response_to_db

## logging
setup_logger('update_logger', 'logs/updater.log', logging.DEBUG)
update_logger = logging.getLogger('update_logger')


# Check the remote database for the last date that is there
def get_batch_delta(api='remedy', batch_size=1):
  '''
    Get last record date in the remote database and set current date as time we want the record for
  '''
  rs = tunnel_db_connect()
  obj=get_model_obj(api)

  # Query
  date_field = getattr(obj, settings[api]['date_scope_field'])
  last_record_date = rs.query(date_field).order_by(date_field.desc()).first()[0]
  time_now = datetime.now()
  rs.close()
  batch_delta = batch_dates(last_record_date.strftime(date_format), time_now.strftime(date_format), batch_size)
  return(batch_delta)
  
def update_db(api='remedy', connection='remote', sleep_time=3):
  # Get dates
  batch_delta = get_batch_delta('remedy', 1)

  for date_range in batch_delta:
    update_logger.info("Polling %s to %s" % (date_range[0], date_range[1]))
    ### poll the current date range for cases
    try:
        response = poll_api(api, date_range[0], date_range[1])
        update_logger.info("Successfully polled api from %s to %s with %s results"%(date_range[0], date_range[1], response["meta"]["length"]))
    except:
        update_logger.error(str(sys.exc_info()[0]) + "Thrown from update_db")
        ### skip to next iteration
        continue
    ### if the api read worked send them to db
    db_result = response_to_db(api, response, connection)
    if db_result[0]:
        ### Everything went ok
        update_logger.info(db_result[1])
    else:
        ### There was an error
        update_logger.error(db_result[1] + "thrown from api_extractor")
    update_logger.debug("sleeping for %s seconds" % (sleep_time))
    sleep(sleep_time)
  update_logger.info("*** Batch extraction for %s to %s complete ***" % (batch_delta[0][0], batch_delta[-1][1]))
  return(True)

# if '__name__' == '__main__':

#     parser = argparse.ArgumentParser()
#     parser.add_argument("-a", "-api", dest="api", default="remedy", required=True, help="select api from live, complaints or archive")
#     parser.add_argument("-s", "--sleep", dest="sleep", default=3, type=int, help="amount of seconds you want between api requests")
#     parser.add_argument("-c", "--connection", dest="connection", default='remote', type=str, help="The connection to draw from the orm settings"
#     args = parser.parse_args()

#     update_db(args.api, args.connection, args.sleep)
