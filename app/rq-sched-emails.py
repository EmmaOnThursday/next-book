from redis import Redis
from rq_scheduler import Scheduler
from datetime import datetime

from rq import Queue
from rq.job import Job
from flask import request, render_template, url_for, Flask
from emailing.email_for_rq_testing import send_recommendation_email
from greting import print_greeting

from model import Book, User, Recommendation, UserBook, connect_to_db, db
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


app = Flask(__name__)


scheduler = Scheduler(connection=Redis())

time = datetime(2016, 3, 3, 2, 10)

scheduler.schedule(
    scheduled_time=time, # Time for first execution, in UTC timezone
    func=send_recommendation_email,        # Function to be queued
    # args = ,
    interval=120,                   # Time before the function is called again, in seconds
    repeat=5                      # Repeat this number of times (None means repeat forever)
)


# 86400 seconds in a day
