from datetime import datetime, timedelta, timezone, time
from time import sleep
from poll_api import get_wsdl_payload, config_wsdl_payload, send_request, parse_xml 
import logging
import argparse
import sys
from config.api_settings import settings
import importlib
from util import *



# Check the remote database for the last date that is there
def get_date_query_range(api='remedy'):
  '''
    Get last record date in the remote database and set current date as time we want the record for
  '''
  tunnel('open')
  rs = gen_session('remote')
  # Query
  last_record_date = rs.query(RemedyCase.call_opened_date).order_by(RemedyCase.call_opened_date.desc()).limit(1)[0]
  time_now = datetime.now()
  format_string = '%d-%m-%Y %H:%M:%S %p'
