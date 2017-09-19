import sys
import xml.etree.ElementTree as etree
import requests
import urllib
import simplejson as json
import re
import argparse

API_ADDRESS = "http://hnsappass07s.glasgow.gov.uk:50700/dswsbobje/qaawsservices/biws?WSDL=1&cuid=FjpUXlkvFAEAWxMAAADn77_nAFBWt.7D"
POST_ADDRESS = "http://hnsappass07s.glasgow.gov.uk:50700/dswsbobje/qaawsservices/queryasaservice/biws?cuid=FrtZVllgYwUAWxMAAAAnMcGXAFBWt.7D&authType=secEnterprise&locale=en_US&timeout=60&ConvertAnyType=false"

def get_xml_body_string(filename):
    xml_string = open(filename, 'r+').read()
    return(xml_string)

def config_query_dates(xml_string, from_date = "08-01-2017", to_date="08-04-2017"):
    parsed_xml = etree.fromstring(xml_string)
    #update from date
    parsed_xml.findall('.//{Cleansing & Parks Remedy Complaints}Enter_value_s__for__Call_Opened_Date_Time_BST___Start_')[0].text = from_date
    parsed_xml.findall('.//{Cleansing & Parks Remedy Complaints}Enter_value_s__for__Call_Opened_Date_Time_BST___End_')[0].text = to_date

    config_xml_string = etree.tostring(parsed_xml, encoding="utf8", method="xml")
    return(config_xml_string)

def send_request(query_string, body, headers = {'content-type': 'text/xml'}):
    response = requests.post(query_string, data=body, headers=headers).content
    return(response)

def parse_xml(xml_string, **kwargs):
   ### read xml
   parsed_xml = etree.fromstring(xml_string) 
   ### access rows
   rows = parsed_xml.findall(".//{Remedy_Complaints}row")
   ### unpack rows into dictionary
   remedy_rows = {}
   for row in rows:
       row_dict = {}
       for item in row:
           row_dict[re.match(r"({.*})(.*)", item.tag)[2].lower()] = item.text
       id = row.findall('./{Remedy_Complaints}Call_Id')[0].text
       remedy_rows[id] = row_dict
   remedy_rows = {"meta": {"length":len(remedy_rows)}, "data" : remedy_rows }
   return(remedy_rows)

if __name__ == "__main__":
    ### parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-sd", "--startdate", dest="startdate", default="09-01-2017", help="format m/d/y ie 09-01-2017")
    parser.add_argument("-ed", "--enddate", dest="enddate", default="09-03-2017", help="format m/d/y ie 09-01-2017")
    parser.add_argument('-w', '--wsdl', dest="wsdl", default="config/remdy_wsdl.xml", help="wsdl config file", required=True)
    args = parser.parse_args()
    ### read xml query payload
    body_string = get_xml_body_string(args.wsdl)
    ### configure XML query payload
    configured_body = config_query_dates(body_string, from_date = args.startdate,  to_date=args.enddate)
    ### Send request and store response
    response = send_request(API_ADDRESS, configured_body)
    ### Parse string XML resposne
    parsed_response = parse_xml(response)
    parsed_response['meta']['start_date'] = args.startdate
    parsed_response['meta']['end_date'] = args.enddate
    ### Print to standard output
    print(parsed_response)

