import os
from sqlalchemy.engine.url import URL
### Set this to default to development

### Try to get environment variables for connection
try:
    remote_pass = os.environ['AZURE_PSQL_PASS']
except:
    remote_pass = None

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
            'port': '5556',
            'username': 'gccadminuser@devpgsql',
            'password': remote_pass, 
            'database': 'gcc-dev-foi',
            'query': {'client_encoding': 'utf8'}}

        }

### Set environment variables
ECHO = False

### App settings


