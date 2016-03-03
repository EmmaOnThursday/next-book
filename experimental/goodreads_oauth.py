from rauth.service import OAuth1Service, OAuth1Session
import os
from server import app
from flask import url_for

GOODREADS_SECRET = os.environ.get("GOODREADS_KEY")
GOODREADS_KEY = os.environ.get("GOODREADS_SECRET")

goodreads = OAuth1Service(
    consumer_key=GOODREADS_KEY,
    consumer_secret=GOODREADS_SECRET,
    name='goodreads',
    request_token_url='http://www.goodreads.com/oauth/request_token',
    authorize_url='http://www.goodreads.com/oauth/authorize',
    access_token_url='http://www.goodreads.com/oauth/access_token',
    base_url='http://www.goodreads.com/'
    )

# from flask-rauth tutorial
@app.route('/redirect')
def redirect():
    return goodreads.authorize(callback=url_for('authorized', _external=True))

@app.route('/authorized')
@github.authorized_handler()
def authorized(response, access_token):
    # handle authorization



request_token, request_token_secret = goodreads.get_request_token(header_auth=True)

authorize_url = goodreads.get_authorize_url(request_token)
print 'Visit this URL in your browser: ' + authorize_url
accepted = 'n'
while accepted.lower() == 'n':
    # you need to access the authorize_link via a browser,
    # and proceed to manually authorize the consumer
    accepted = raw_input('Have you authorized me? (y/n) ')

# these values are what you need to save for subsequent access.
ACCESS_TOKEN = session.access_token
ACCESS_TOKEN_SECRET = session.access_token_secret




