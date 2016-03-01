"""Every day, update the database at 12am to add a delivery date to one rec for each user."""

import random
import datetime as dt
from server import app
from model import connect_to_db, db, Book, User, Recommendation, Subject, UserBook, BookSubject

from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


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

def generate_recommendation_delivery_dates():
    active_users = User.query.filter(User.paused==0).all()
    # print len(active_users)

    for user in active_users:
        undelivered_recs = Recommendation.query.filter(Recommendation.userbook.has(UserBook.user_id==user.user_id), 
            Recommendation.date_provided == None).all()
        today = random.choice(undelivered_recs)
        today.date_provided = dt.date.today()
        db.session.add(today)

    db.session.commit()


#time is in UTC
scheduler.add_job(generate_recommendation_delivery_dates, trigger='cron', hour='8', minute='1')


###### FUNCTION CALLS ###### 
connect_to_db(app)
# generate_recommendation_delivery_dates()