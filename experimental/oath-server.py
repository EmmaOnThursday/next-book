
import random
import datetime as dt
import os
import requests
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Book, User, Recommendation, Subject, UserBook, BookSubject
from sqlalchemy import desc

from rauth.service import OAuth1Service, OAuth1Session

app = Flask(__name__)

app.secret_key = "ABC"

redirect_uri = 'http://78d57001.ngrok.io/'

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
print goodreads
request_token = goodreads.get_request_token(header_auth=True)



# authorize_url = goodreads.get_authorize_url(request_token)
# print 'Visit this URL in your browser: ' + authorize_url
# accepted = 'n'
# while accepted.lower() == 'n':
#     # you need to access the authorize_link via a browser,
#     # and proceed to manually authorize the consumer
#     accepted = raw_input('Have you authorized me? (y/n) ')

# # these values are what you need to save for subsequent access.
# ACCESS_TOKEN = session.access_token
# ACCESS_TOKEN_SECRET = session.access_token_secret





