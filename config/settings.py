import os
from sqlalchemy.engine.url import URL

### Try to get environment variables for connection
try:
    remote_pass = os.environ['AZURE_PSQL_PASS']
except:
    remote_pass = None


api_settings = {
        "archive": {"url":"http://hnsappass07s.glasgow.gov.uk:50700/dswsbobje/qaawsservices/queryasaservice/biws?cuid=Ftaew1mh6QMAbV8AAAAnMMSnAFBWt.7D&authtype=secenterprise&locale=en_us&timeout=60&convertanytype=false",
                    "filename":"config/wsdl/archive_wsdl.xml",
                    "namespace":"RemedyArchive",
                    "row_selector":"row",
                    "row_id": "Call_Id",
                    "start": "Enter_value_s__for__Call_Opened_Time___Start_",
                    "end": "Enter_value_s__for__Call_Opened_Time___End_",
                    "date_fields":['bulk_uplift_date','est_resp_date','est_resp_date_bst','date_1st_contact_made','date_1st_contact_made_bst','date_paid','date_paid_bst','call_opened_date','call_opened_date_bst','call_opened_date_time','call_opened_time','call_opened_date_time_bst','call_opened_time_bst','call_closed_date','call_closed_date_bst','call_closed_date_time','call_closed_date_time_bst','date_time_last_modified','date_time_last_modified_bst','date_time_sla_warning','date_time_sla_warning_bst','date_time_sla_violation','date_time_sla_violation_bst','date_time_manual_closed','date_time_manual_closed_bst','manual_closed___system_closed_date','time_taken','original_create_date','original_create_date_bst','original_create_time','original_create_time_bst']
                    , "date_scope_field":"original_create_time" 
                    },
        "remedy": {"url":"http://hnsappass07s.glasgow.gov.uk:6405/dswsbobje/qaawsservices/queryasaservice/biws?cuid=Fp.5wFkumwsAbV8AAAAnMsanAFBWt.7D&authType=secEnterprise&locale=en_US&ConvertAnyType=false",
                    "filename":"config/wsdl/live_wsdl.xml",
                    "namespace":"RemedyLiveAll",
                    "row_selector":"row",
                    "row_id": "Call_Id",
                    "start": "Enter_value_s__for__Call_Opened_Date___Start_",
                    "end": "Enter_value_s__for__Call_Opened_Date___End_",
                    "date_fields":['bulk_uplift_date','est_resp_date','est_resp_date_bst','date_1st_contact_made','date_1st_contact_made_bst','date_paid','date_paid_bst','call_opened_date','call_opened_date_bst','call_opened_date_time','call_opened_time','call_opened_date_time_bst','call_opened_time_bst','call_closed_date','call_closed_date_bst','call_closed_date_time','call_closed_date_time_bst','date_time_last_modified','date_time_last_modified_bst','date_time_sla_warning','date_time_sla_warning_bst','date_time_sla_violation','date_time_sla_violation_bst','date_time_manual_closed','date_time_manual_closed_bst','manual_closed___system_closed_date','time_taken']
                    , "date_scope_field":"call_opened_time" 
                    },
        "archive_test": {"url":"http://hnsappass07s.glasgow.gov.uk:6405/dswsbobje/qaawsservices/queryasaservice/biws?cuid=Ftaew1mh6QMAbV8AAAAnMMSnAFBWt.7D&authType=secEnterprise&locale=en_US&ConvertAnyType=false",
                    "filename":"config/wsdl/archive_wsdl.xml",
                    "namespace":"RemedyArchive",
                    "row_selector":"row",
                    "row_id": "Call_Id",
                    "start": "Enter_value_s__for__Original_Create_Time___Start_",
                    "end": "Enter_value_s__for__Original_Create_Time___End_",
                    "date_fields":['bulk_uplift_date','est_resp_date','est_resp_date_bst','date_1st_contact_made','date_1st_contact_made_bst','date_paid','date_paid_bst','call_opened_date','call_opened_date_bst','call_opened_date_time','call_opened_time','call_opened_date_time_bst','call_opened_time_bst','call_closed_date','call_closed_date_bst','call_closed_date_time','call_closed_date_time_bst','date_time_last_modified','date_time_last_modified_bst','date_time_sla_warning','date_time_sla_warning_bst','date_time_sla_violation','date_time_sla_violation_bst','date_time_manual_closed','date_time_manual_closed_bst','manual_closed___system_closed_date','time_taken']
                    , "date_scope_field":"call_opened_time" 
                    },
        "remedy_test": {"url":"http://hnsappass07s.glasgow.gov.uk:6405/dswsbobje/qaawsservices/queryasaservice/biws?cuid=Ftaew1kDpwIAbV8AAAAHEsanAFBWt.7D&authType=secEnterprise&locale=en_US&ConvertAnyType=false",
                    "filename":"config/wsdl/live_wsdl.xml",
                    "namespace":"RemedyLiveAll",
                    "row_selector":"row",
                    "row_id": "Call_Id",
                    "start": "Enter_value_s__for__Call_Opened_Time___Start_",
                    "end": "Enter_value_s__for__Call_Opened_Time___End_",
                    "date_fields":['bulk_uplift_date','est_resp_date','est_resp_date_bst','date_1st_contact_made','date_1st_contact_made_bst','date_paid','date_paid_bst','call_opened_date','call_opened_date_bst','call_opened_date_time','call_opened_time','call_opened_date_time_bst','call_opened_time_bst','call_closed_date','call_closed_date_bst','call_closed_date_time','call_closed_date_time_bst','date_time_last_modified','date_time_last_modified_bst','date_time_sla_warning','date_time_sla_warning_bst','date_time_sla_violation','date_time_sla_violation_bst','date_time_manual_closed','date_time_manual_closed_bst','manual_closed___system_closed_date','time_taken']
                    , "date_scope_field":"call_opened_time" 
                    },
        "remedy_update": {"url":"http://hnsappass07s.glasgow.gov.uk:6405/dswsbobje/qaawsservices/queryasaservice/biws?cuid=FmcqulopPQcAelQAAADn8MinAFBWt.7D&authType=secEnterprise&locale=en_US&ConvertAnyType=false",
                    "filename":"config/wsdl/update_wsdl.xml",
                    "namespace":"RemedyLiveUpdate",
                    "row_selector":"row",
                    "row_id": "Call_Id",
                    "start": "Enter_value_s__for__Date_Time_Last_Modified___Start_",
                    "end": "Enter_value_s__for__Date_Time_Last_Modified___End_",
                    "date_fields":['bulk_uplift_date','est_resp_date','est_resp_date_bst','date_1st_contact_made','date_1st_contact_made_bst','date_paid','date_paid_bst','call_opened_date','call_opened_date_bst','call_opened_date_time','call_opened_time','call_opened_date_time_bst','call_opened_time_bst','call_closed_date','call_closed_date_bst','call_closed_date_time','call_closed_date_time_bst','date_time_last_modified','date_time_last_modified_bst','date_time_sla_warning','date_time_sla_warning_bst','date_time_sla_violation','date_time_sla_violation_bst','date_time_manual_closed','date_time_manual_closed_bst','manual_closed___system_closed_date','time_taken']
                    , "date_scope_field":"date_time_last_modified" 
                    },

        }

connections = {
        "local":{
            'drivername': 'postgres',
            'host': 'localhost',
            'port': '5432',
            'username': 'devonwalshe',
            'password': '',
            'database': 'remedy',
            'query': {'client_encoding': 'utf8'}}
,
        "remote":{
            'drivername': 'postgres',
            'host': 'localhost',
            'port': '5555',
            'username': 'gccadminuser@devpgsql',
            'password': remote_pass, 
            'database': 'gcc-dev-foi',
            'query': {'client_encoding': 'utf8'}}
,
        "test":{
            'drivername': 'postgres',
            'host': 'localhost',
            'port': '5432',
            'username': 'devonwalshe',
            'password': '',
            'database': 'remedy',
            'query': {'client_encoding': 'utf8'}}

        }

### Set environment variables
ECHO = False

fetch_date_format = '%m-%d-%Y %I:%M:%S %p'
parse_date_format = '%Y-%m-%dT%H:%M:%S.%f'
crawl_delay = 3

