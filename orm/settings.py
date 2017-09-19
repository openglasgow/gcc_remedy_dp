import os
from sqlalchemy.engine.url import URL
### Set this to default to development
os.environ['ENV'] = "development"

## Dev settings
if os.environ['ENV'] == "development":
    ### Set up database 
    DATABASE = {
            'drivername': 'postgres',
            'host': 'localhost',
            'port': '5432',
            'username': 'devonwalshe',
            'password': '',
            'database': 'remedy',
            'query': {'client_encoding': 'utf8'}}
## Docker settings
if os.environ['ENV'] == "docker":
    ### Set up database 
    DATABASE = {
            'drivername': 'postgres',
            'host': '67.207.84.204',
            'port': '5432',
            'username': 'gcc_data',
            'password': os.environ['PG_PASS'],
            'database': 'remedy'}
    ### TODO More docker specific settings here



### Set environment variables
os.environ['POSTGRES_URL'] = str(URL(**DATABASE))
ECHO = False

### App settings


