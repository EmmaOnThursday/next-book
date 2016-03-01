"""Every day, update the database at 12am to add a delivery date to one rec for each user."""

import random
import datetime as dt
import os

# app imports
from server import app
from model import connect_to_db, db, Book, User, Recommendation, Subject, UserBook, BookSubject

# scheduler imports
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

# email imports
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText



# set up scheduler
jobstores = {
    'default': SQLAlchemyJobStore(url='postgresql:///nextbook')
}

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)

# define functions to schedule

def generate_recommendation_delivery_dates():
    """For each user, 'deliver' one recommendation per day."""
    active_users = User.query.filter(User.paused==0).all()
    # print len(active_users)

    for user in active_users:
        undelivered_recs = Recommendation.query.filter(Recommendation.userbook.has(UserBook.user_id==user.user_id), 
            Recommendation.date_provided == None).all()
        today = random.choice(undelivered_recs)
        today.date_provided = dt.date.today()
        db.session.add(today)

    db.session.commit()



def send_recommendation_email():
    """Send a recommendation email to each active user with today's book."""
    fromaddr = os.environ.get("NEXTBOOK_GMAIL")
    username = fromaddr
    password = os.environ.get("NEXTBOOK_GMAIL_PW")  
    
    active_users = User.query.filter(User.paused==0).all()
    if active_users:
        for user in active_users:
            today_rec = Recommendation.query.filter(
                Recommendation.userbook.has(UserBook.user_id==user.user_id),
                Recommendation.date_provided==dt.date.today()).first()
            rec_title = today_rec.userbook.book.title
            rec_link = today_rec.userbook.book.goodreads_url
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = user.email
            msg['Subject'] = "Today\'s Recommendation!"
            body = "Here's today's recommendation!\n"+rec_title+": "+rec_link+"\nWith love from NextBook"
            msg.attach(MIMEText(body, 'plain'))

            # The actual mail send
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.login(username,password)
            text = msg.as_string()
            server.sendmail(fromaddr, msg['To'], text)
            server.quit()


#time is in UTC
scheduler.add_job(generate_recommendation_delivery_dates, trigger='cron', hour='8', minute='1')
scheduler.add_job(send_recommendation_email, trigger='cron', hour='20')


###### FUNCTION CALLS ###### 
connect_to_db(app)
scheduler.start()
# generate_recommendation_delivery_dates()
# send_recommendation_email()
