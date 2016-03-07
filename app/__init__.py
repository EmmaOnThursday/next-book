""" Server for NextBook """

import random
import datetime as dt
import os

from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import desc
from jinja2 import StrictUndefined

from redis import Redis
from datetime import datetime
from rq import Queue
from rq.job import Job

from model import connect_to_db, db, Book, User, Recommendation, Subject, UserBook, BookSubject
from api_calls.new_user_setup import new_user_full_setup
from test_mod import test_function


app = Flask(__name__)

q = Queue(connection=Redis(), default_timeout=600)

# Prevents undefined variables in Jinja from failing silently.
app.jinja_env.undefined = StrictUndefined

# keys & secrets
goodreads_key=os.environ['GOODREADS_KEY']
# goodreads_secret=os.environ['GOODREADS_SECRET']

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

gr_user_id = "16767050"

current_user_id = 1

print goodreads_key
print gr_user_id
print current_user_id

######### ROUTES ######### 

@app.route("/")
def index():
    """Landing page; includes login.""" 

    return render_template("home.html")


@app.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    """For new users only: sign-up page."""  

    # if form has been submitted...
    if request.method == 'POST':
        #save all variables from form
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        email = request.form.get('email')
        password  = request.form.get('password')
        goodreads_uid = int(request.form.get('goodreads_uid'))
        rec_frequency = 1
        user_id = 1

        # try to instantiate user based on email from form
        user = User.query.filter(User.email == email).all()

        # if user already in DB, redirect to home page
        if user != []:
            flash("Looks like you've already signed up! Please log in.")
            return redirect(url_for('index'))
        
        # if user does not exist, create & commit to DB
        else:
            new_user = User(email=email, password=password, 
                f_name=f_name, l_name=l_name,
                goodreads_uid=goodreads_uid, rec_frequency=rec_frequency,
                sign_up_date=dt.datetime.now(), paused=0, user_id=user_id)
            print new_user
            db.session.add(new_user)
            db.session.commit()
            flash("Welcome to NextBook!")
            session['current_user_id'] = new_user.user_id
            
            ## new user setup ###
            q = Queue(connection=Redis())

            results = q.enqueue_call(new_user_full_setup, 
                args = [gr_user_id, new_user.user_id, goodreads_key],
                ttl=86400)

            session['new_user_job_id'] = results.get_id()
            
            return redirect(url_for('recommendations'))    

    return render_template('sign-up.html')



@app.route("/get_signup_status")
def get_new_user_job_results():
    """Returns status of redis job to see if recommendations are available."""

    # get job status from Redis via RQ
    job_id = session.get("new_user_job_id")
    job = q.fetch_job(job_id)
    if job.result == None:
        return None
    else:
        # return recs
        current_user = User.query.get(session['current_user_id'])

        query = Recommendation.query.filter(Recommendation.date_provided <= dt.datetime.now(), 
            Recommendation.userbook.has(user_id=current_user_id))

        recs_to_date=query.order_by(desc(Recommendation.date_provided)).all()

        if len(recs_to_date) == 0:
            recs_to_show = None
            today_rec = None
        else:
            if recs_to_date[0].date_provided.date() == dt.date.today():
                recs_to_show = recs_to_date[1:]
                today_rec = recs_to_date[0]
            else:
                recs_to_show = recs_to_date
                today_rec = False
        return recs_to_show, today_rec

    # respond to ajax call asking for recommendation list
    # move @rec python code up here to query db
    # ajax will ask this route if job is done yet



@app.route("/loading")
def loading():
    """For new users only: waiting for recommendations to generate."""
    
    return render_template("loading.html")



@app.route("/recommendations")
def recommendations():
    """List of all recommendations; allows users to leave feedback on recommendations."""

    current_user = User.query.get(1)

    query = Recommendation.query.filter(Recommendation.date_provided <= dt.datetime.now(), 
        Recommendation.userbook.has(user_id=current_user_id))

    recs_to_date=query.order_by(desc(Recommendation.date_provided)).all()

    if len(recs_to_date) == 0:
        recs_to_show = None
        today_rec = None
    else:
        if recs_to_date[0].date_provided.date() == dt.date.today():
            recs_to_show = recs_to_date[1:]
            today_rec = recs_to_date[0]
        else:
            recs_to_show = recs_to_date
            today_rec = False

    return render_template("recommendation-list.html", recs_to_date=recs_to_show, today_rec=today_rec)



@app.route("/recommendations/<int:rec_id>")
def rec_details(rec_id):
    """Provides details on each specific recommendation."""
    
    current_rec = Recommendation.query.get(rec_id)
    print current_rec.response

    return render_template("recommendation-detail.html", rec=current_rec)



@app.route("/recommendations/<int:rec_id>/user-feedback", methods=['POST'])
def record_user_feedback(rec_id):
    """Takes in user feedback from recommendations & saves to Postgres."""

    response = request.form.get('response')
    if response=='read-now':
        current_user = User.query.get(current_user_id)
        current_user.paused = 1
        current_user.paused_date = dt.datetime.today()
        db.session.add(current_user)
        
    rec_id = request.form.get('rec_id')
    current_rec = Recommendation.query.get(rec_id)
    current_rec.response = response # get response from user input

    db.session.add(current_rec)
    db.session.commit()

    button_to_color = {'rec_id': rec_id, 'button': response}

    return jsonify(button_to_color)




@app.route("/account")
def account_page():
    """Account preferences page."""
    # pause account, change rec frequency, change email, pw, etc
    current_user = User.query.get(current_user_id)
    status = 0
    if current_user.paused == 1:
        status = "You paused your account on "+ str(current_user.paused_date)

    return render_template("account.html", User=current_user, status=status)




#### APP MAINTENANCE ROUTES ####
# need to send emails to all users at noon
# need to update database daily at midnight
# scheduler.start()



#### FUNCTION CALLS ####
# if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    # app.debug = True

connect_to_db(app)

# Use the DebugToolbar
DebugToolbarExtension(app)

# app.run()

