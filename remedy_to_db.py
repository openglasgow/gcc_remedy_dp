from orm.orm import db_connect, create_tables, Base
from orm.models import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone, time
from time import sleep
from poll_remedy_api import API_ADDRESS, get_xml_body_string, config_query_dates, send_request, parse_xml 
import logging
import argparse
import sys

### logging config
logging.basicConfig(filename="remedy_to_db.log", level=logging.DEBUG, format='%(asctime)s -- %(levelname)s: %(message)s')

## setup connection
def gen_session():
    engine = db_connect()
    create_tables(engine, Base)
    Session = sessionmaker(bind=engine)
    session = Session()
    return(session)

def poll_api(wsdl = "config/remedy_wsdl.xml", start_date=datetime.strftime(datetime.today() - timedelta(days = 1), '%m-%d-%Y'), end_date=datetime.strftime(datetime.today(), '%m-%d-%Y')):
    ### Get response from api
    xml_query_payload = get_xml_body_string(wsdl)
    configured_payload = config_query_dates(xml_query_payload, start_date, end_date)
    response = send_request(API_ADDRESS, configured_payload)
    parsed_response = parse_xml(response)
    parsed_response['meta']['start_date'] = start_date
    parsed_response['meta']['end_date'] = end_date    
    return(parsed_response)


def parse_dates(remedy_case):
    try:
        remedy_case["call_opened_date_time"] = datetime.strptime(remedy_case["call_opened_date_time"], "%Y-%m-%dT%H:%M:%S.%f")
    except:
        remedy_case["call_opened_date_time"] = None
    try:
        remedy_case["call_opened_date_time_bst"] = datetime.strptime(remedy_case["call_opened_date_time_bst"], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone(timedelta(hours=1)))
    except:
        remedy_case["call_opened_date_time_bst"] = None
    try:
        remedy_case["call_closed_date_time_bst"] = datetime.strptime(remedy_case["call_closed_date_time_bst"], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone(timedelta(hours=1)))
    except:
        remedy_case["call_closed_date_time_bst"] = None
    try:
        remedy_case["date_time_manual_closed_bst"] = datetime.strptime(remedy_case["call_opened_date_time"], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone(timedelta(hours=1)))
    except:
        remedy_case["date_time_manual_closed_bst"] = None
    return(remedy_case)

def response_to_db(parsed_response):
    ## Setup session
    session = gen_session()
    ## place data in session
    remedy_cases = parsed_response["data"]
    try:
        for id,case in remedy_cases.items():
            case = parse_dates(case)
            remedy_case = RemedyCase(**case)
            session.add(remedy_case)
        session.commit(  )
        result = (True, "%s cases written to the database"%(parsed_response["meta"]["length"]))
    except:
        e = sys.exc_info()[0]
        result = (False, e)
    finally:
        session.close()
        return(result)


def batch_dates(start_date = "09-01-2017", end_date= "09-01-2017", batch_size=3):
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

def remedy_extractor(batch_size=3, sleep_time = 3,  start_date = "09-01-2017", end_date="09-05-2017"):
    logging.info("*** Batch extraction starting with batch size of %s, sleep time of %s, from %s to %s." %(batch_size, sleep_time, start_date, end_date))
    ### Generate a tuple of date ranges, then for each one
    dates_list = batch_dates(start_date, end_date, batch_size)
    ### iterate through the batch dates and put the results in the db
    for date_range in dates_list:
        logging.info("Polling %s to %s" % (date_range[0], date_range[1]))
        ### poll the current date range for cases
        try:
            response = poll_api("config/remedy_wsdl.xml", date_range[0], date_range[1])
            logging.info("Successfully polled api from %s to %s with %s results"%(date_range[0], date_range[1], response["meta"]["length"]))
        except:
            logging.error(sys.exc_info()[0])
            ### skip to next iteration
            continue
        ### if the api read worked send them to db
        db_result = response_to_db(response)
        if db_result[0]:
            ### Everything went ok
            logging.info(db_result[1])
        else:
            ### There was an error
            logging.error(db_result[1])
        logging.debug("sleeping for %s seconds" % (sleep_time))
        sleep(sleep_time)
    logging.info("*** Batch extraction for %s to %s complete ***" % (start_date, end_date))
    return(True)

if __name__ == "__main__":

    ### Set up cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-sd", "--startdate", dest="startdate", default="09-01-2017", help="format m/d/y ie 09-01-2017", required=True)
    parser.add_argument("-ed", "--enddate", dest="enddate", default="09-03-2017", help="format m/d/y ie 09-01-2017", required=True)
    parser.add_argument("-s", "--sleep", dest="sleep", default=3, type=int, help="amount of seconds you want between api requests")
    parser.add_argument("-b", "--batchsize", dest="batchsize", default=5, type=int, help="days interval between start and end dates to batch api requests")
    args = parser.parse_args()
    print("extracting remedy cases from %s to %s, this may take a while..." % (args.startdate, args.enddate))
    remedy_extractor(args.batchsize, args.sleep, args.startdate, args.enddate)
    print("All done!") 
