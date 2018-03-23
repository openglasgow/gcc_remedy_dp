import sys
import xml.etree.ElementTree as etree
import requests
import re
from config.settings import api_settings, fetch_date_format
from datetime import datetime, timedelta
from .util import Util

class BoFetcher(object):
  def __init__(self, api, from_datetime, to_datetime, date_format=fetch_date_format, settings=api_settings, logger=None):
    self.settings = settings
    self.api = api
    self.date_format = date_format
    self.from_datetime = Util().validate_date("fetch", from_datetime)
    self.to_datetime = Util().validate_date("fetch", to_datetime)
    
    ## Validate api key
    try:
      self.conf = self.settings[self.api]
      self.wsdl_payload = self.set_wsdl_payload()
    except KeyError:
      raise KeyError("api key \"{}\" not found in settings".format(self.api))
    
    ## Configure payload
    self.wsdl_payload = self.config_wsdl_payload()
    self.logger = logger
    # Validate dates

  def set_wsdl_payload(self):
      xml_string = open(self.conf["filename"], 'r+').read()
      return(xml_string)

  def config_wsdl_payload(self):
      # Parse wsdl payload
      parsed_xml = etree.fromstring(self.wsdl_payload)
      #update from date
      parsed_xml.findall(".//{%s}%s" % (self.settings[self.api]['namespace'], self.settings[self.api]['start_selector']))[0].text = self.from_datetime
      parsed_xml.findall(".//{%s}%s" % (self.settings[self.api]['namespace'], self.settings[self.api]['end_selector']))[0].text = self.to_datetime
      # back to string
      config_xml_string = etree.tostring(parsed_xml, encoding="utf8", method="xml")
      return(config_xml_string)


  def send_request(self):
      headers = {'content-type': 'text/xml'}
      # TODO - logging
      # self.logger("Sending request to BO api {} with dates {} to {}".format(self.api, self.from_datetime, self.to_datetime))
      try:
        response = requests.post(self.conf['url'], data=self.wsdl_payload, headers=headers).content
      except:
        e = sys.exc_info()[0]
        # TODO - logging
        raise e("Problem fetching the request")
      try:
        parsed_response = self.parse_response(response)
      except:
        # TODO - logging
        e = sys.exc_info()[0]
        raise e("Problem with parsing the response")
      
      parsed_response = {"meta": {
                              "length":len(parsed_response), 
                              "from_datetime": datetime.strptime(self.from_datetime, self.date_format),
                              "to_datetime": datetime.strptime(self.to_datetime, self.date_format),
                              "api": self.api,
                              "url": self.conf['url']
                              }, 
                     "data" : parsed_response}
      # TODO - logging
      self.response = parsed_response
      return(True)

  def parse_response(self, response, **kwargs):
     ### read xml
     parsed_xml = etree.fromstring(response) 
     ### access rows
     rows = parsed_xml.findall(".//{{{}}}{}".format(self.conf['namespace'], self.conf['row_selector']))
     ### unpack rows into dictionary
     parsed_rows = {}
     for row in rows:
         row_dict = {}
         for item in row:
             row_dict[re.match(r"({.*})(.*)", item.tag)[2].lower()] = item.text
         id = row.findall('./{{{}}}{}'.format(self.conf['namespace'], self.conf['row_id']))[0].text
         parsed_rows[id] = row_dict

     # TODO - logging
     return(parsed_rows)

  # def poll_api(api="live", start_date=datetime.strftime(datetime.today() - timedelta(days = 1), '%m-%d-%Y'), end_date=datetime.strftime(datetime.today(), '%m-%d-%Y')):
  #     ### Get response from api
  #     xml_query_payload = get_wsdl_payload(api)
  #     configured_payload = config_wsdl_payload(xml_query_payload, api, start_date, end_date)
  #     response = send_request(settings[api]["url"], configured_payload)
  #     ### TODO do some error checking of the response
  #     parsed_response = parse_xml(api, response)
  #     parsed_response['meta']['start_date'] = start_date
  #     parsed_response['meta']['end_date'] = end_date
  #     return(parsed_response)


# if __name__ == "__main__":
#     ### parse arguments
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-a", "--api", dest="api", default="live", required=True, help="Choose from archive, live or complaints apis")
#     parser.add_argument("-sd", "--startdate", dest="startdate", default="09-01-2017", help="format m/d/y ie 09-01-2017")
#     parser.add_argument("-ed", "--enddate", dest="enddate", default="09-03-2017", help="format m/d/y ie 09-01-2017")
#     args = parser.parse_args()
#     ### read xml query payload
#     body_string = get_wsdl_payload(args.api)
#     ### configure XML query payload
#     configured_body = config_wsdl_payload(body_string, args.api,  from_date = args.startdate,  to_date=args.enddate)
#     ### Send request and store response
#     response = send_request(settings[args.api]['url'], configured_body)
#     if response == b'':
#       sys.exit("empty response")
#     ### Parse string XML resposne
#     parsed_response = parse_xml(args.api, response)
#     parsed_response['meta']['start_date'] = args.startdate
#     parsed_response['meta']['end_date'] = args.enddate
#     ### Print to standard output
#     print(json.dumps(parsed_response))

