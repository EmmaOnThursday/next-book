import os

from redis import Redis
from rq_scheduler import Scheduler
from datetime import datetime

from rq import Queue
from rq.job import Job
from flask import request, render_template, url_for, Flask
from emailing.send_emails import send_recommendation_email

from model import Book, User, Recommendation, UserBook, connect_to_db, db
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


app = Flask(__name__)


scheduler = Scheduler(connection=Redis())

time = datetime(2016, 3, 3, 1, 15)

scheduler.schedule(
    scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
    func=send_recommendation_email,                     # Function to be queued
    args=["Emma"],             # Arguments passed into function when executed
    interval=60,                   # Time before the function is called again, in seconds
    repeat=5                      # Repeat this number of times (None means repeat forever)
)




