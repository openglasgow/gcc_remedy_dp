import sys
import xml.etree.ElementTree as etree
import requests
import urllib
import simplejson as json
import re
import argparse
from config.api_settings import settings 

def get_wsdl_payload(api):
    xml_string = open(settings[api]["filename"], 'r+').read()
    return(xml_string)

def config_wsdl_payload(xml_string, api="live",  from_date = "08-01-2017", to_date="08-04-2017"):
    parsed_xml = etree.fromstring(xml_string)
    #update from date
    parsed_xml.findall(".//{%s}%s" % (settings[api]['namespace'], settings[api]['start_selector']))[0].text = from_date
    parsed_xml.findall(".//{%s}%s" % (settings[api]['namespace'], settings[api]['end_selector']))[0].text = to_date

    config_xml_string = etree.tostring(parsed_xml, encoding="utf8", method="xml")
    return(config_xml_string)

def send_request(url, body, headers = {'content-type': 'text/xml'}):
    response = requests.post(url, data=body, headers=headers).content
    return(response)

def parse_xml(api, xml_string, **kwargs):
   ### read xml
   parsed_xml = etree.fromstring(xml_string) 
   ### access rows
   rows = parsed_xml.findall(".//{%s}%s" % (settings[api]['namespace'], settings[api]['row_selector']))
   ### unpack rows into dictionary
   parsed_rows = {}
   for row in rows:
       row_dict = {}
       for item in row:
           row_dict[re.match(r"({.*})(.*)", item.tag)[2].lower()] = item.text
       id = row.findall('./{%s}Call_Id' % (settings[api]['namespace']))[0].text
       parsed_rows[id] = row_dict
   parsed_rows = {"meta": {"length":len(parsed_rows)}, "data" : parsed_rows }
   return(parsed_rows)

if __name__ == "__main__":
    ### parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--api", dest="api", default="live", required=True, help="Choose from archive, live or complaints apis")
    parser.add_argument("-sd", "--startdate", dest="startdate", default="09-01-2017", help="format m/d/y ie 09-01-2017")
    parser.add_argument("-ed", "--enddate", dest="enddate", default="09-03-2017", help="format m/d/y ie 09-01-2017")
    args = parser.parse_args()
    ### read xml query payload
    body_string = get_wsdl_payload(args.api)
    ### configure XML query payload
    configured_body = config_wsdl_payload(body_string, args.api,  from_date = args.startdate,  to_date=args.enddate)
    ### Send request and store response
    response = send_request(settings[args.api]['url'], configured_body)
    if response == b'':
      sys.exit("empty response")
    ### Parse string XML resposne
    parsed_response = parse_xml(args.api, response)
    parsed_response['meta']['start_date'] = args.startdate
    parsed_response['meta']['end_date'] = args.enddate
    ### Print to standard output
    print(json.dumps(parsed_response))

