import os
from functools import wraps
from flask import Flask, jsonify, request
from .crawler import BoCrawler
from orm.models import RemedyCase, RemedyTest, ArchiveCase, ArchiveTest, Base
# App 
app = Flask(__name__)
app.config['DEBUG'] = True


# Auth
def check_auth(username, password):
  return username==os.environ['AUTH_USER'] and password==os.environ['AUTH_PASSWORD']

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# API
@app.route('/schedule', methods=['POST'])
@requires_auth
def schedule():
  # get post data as json
  body = request.get_json()
  if set(['api', 'connection', 'model']).issubset(body.keys()):
    crawler = BoCrawler(body['api'], body['connection'], eval(body['model']))

  if 'batch_delta' in body.keys():
    crawler.batch_list = crawler.get_batch_delta()

  elif 'start_datetime' and 'end_datetime' in body.keys():
    start_datetime = crawler.util.validate_date('fetch', start_datetime)
    end_datetime = crawler.util.validate_date('fetch', end_datetime)
    crawler.batch_list = crawler.util.batch_dates(start_datetime, end_datetime)

  elif 'period' in body.keys():
    crawler.set_range(body['period'])

  else:
    crawler.set_range('2days')
  # TODO - Turn this into a job
  crawler.crawl()
  # return
  return jsonify(crawler.batch_list)