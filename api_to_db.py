from datetime import datetime, timedelta, timezone, time
from time import sleep
from poll_api import get_wsdl_payload, config_wsdl_payload, send_request, parse_xml 
import logging
import argparse
import sys
from config.api_settings import settings
import importlib
from util import *

### logging config
setup_logger('extraction_logger', 'logs/extraction.log', logging.DEBUG)
extraction_logger = logging.getLogger('extraction_logger')


def poll_api(api="live", start_date=datetime.strftime(datetime.today() - timedelta(days = 1), '%m-%d-%Y'), end_date=datetime.strftime(datetime.today(), '%m-%d-%Y')):
    ### Get response from api
    xml_query_payload = get_wsdl_payload(api)
    configured_payload = config_wsdl_payload(xml_query_payload, api, start_date, end_date)
    response = send_request(settings[api]["url"], configured_payload)
    ### TODO do some error checking of the response
    parsed_response = parse_xml(api, response)
    parsed_response['meta']['start_date'] = start_date
    parsed_response['meta']['end_date'] = end_date
    return(parsed_response)


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


def api_extractor(api="live", batch_size=3, sleep_time = 3,  start_date = "01-01-2017", end_date="01-02-2017", connection="local"):
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

if __name__ == "__main__":
    ### Set up cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "-api", dest="api", default="live", required=True, help="select api from live, complaints or archive")
    parser.add_argument("-sd", "--startdate", dest="startdate", default="09-01-2017", help="format m/d/y ie 09-01-2017", required=True)
    parser.add_argument("-ed", "--enddate", dest="enddate", default="09-03-2017", help="format m/d/y ie 09-01-2017", required=True)
    parser.add_argument("-s", "--sleep", dest="sleep", default=3, type=int, help="amount of seconds you want between api requests")
    parser.add_argument("-b", "--batchsize", dest="batchsize", default=5, type=int, help="days interval between start and end dates to batch api requests")
    parser.add_argument("-c", "--connection", dest="connection", default='local', type=str, help="The connection to draw from the orm settings")
    args = parser.parse_args()
    print("extracting remedy cases from %s to %s, this may take a while..." % (args.startdate, args.enddate))
    api_extractor(args.api, args.batchsize, args.sleep, args.startdate, args.enddate, args.connection)
    print("All done!") 
