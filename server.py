""" Server for NextBook """

import random
import datetime as dt
import os

from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import desc
from jinja2 import StrictUndefined
from celery import Celery

# from scheduled_functions import scheduler, send_recommendation_email, generate_recommendation_delivery_dates
from model import connect_to_db, db, Book, User, Recommendation, Subject, UserBook, BookSubject
from api_calls.new_user_api_calls import get_shelves, get_books_from_shelves, add_book_to_library, add_userbook_to_userbooks


app = Flask(__name__)

# Prevents undefined variables in Jinja from failing silently.
app.jinja_env.undefined = StrictUndefined

# Celery setup
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# keys & secrets
goodreads_key=os.environ['GOODREADS_KEY']
goodreads_secret=os.environ['GOODREADS_SECRET']

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# need to get user's GR id from oauth:
# user Goodreads OAuth-ID API method
# https://www.goodreads.com/api/auth_user
# http method = get
gr_user_id = "16767050"

# after use has logged in:
# get user id from session or whatever...
current_user_id = 1

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
        rec_frequency = int(request.form.get('rec_frequency'))

        # try to instantiate user based on email from form
        user = User.query.filter(User.email == email).all()

        # if user already in DB, redirect to login page
        if user != []:
            flash("Looks like you've already signed up! Please log in.")
            return redirect(url_for('index'))
        
        # if user does not exist, create & commit to DB
        else:
            new_user = User(email=email, password=password, 
                f_name=f_name, l_name=l_name,
                goodreads_uid=goodreads_uid, rec_frequency=rec_frequency,
                sign_up_date=dt.datetime.now(), paused=0)
            print new_user
            db.session.add(new_user)
            db.session.commit()
            flash("Welcome to NextBook!")

            return redirect(url_for('loading'))    

    return render_template('sign-up.html')



# get user's books from Goodreads & create recommendations
@celery.task
def new_user_setup(gr_user_id):
    shelves = get_shelves(gr_user_id)
    book_list = get_books_from_shelves(shelves)
    
    # check if book in library; if not, add to library
    add_book_to_library(book_list)
    
    # add book to UserBook table
    add_userbook_to_userbooks(book_list, gr_user_id)

    # get subjects for all new books
    # generate recommendations
    # return: send user an email


@app.route("/loading")
def loading():
    """For new users only: waiting for recommendations to generate."""
    
    return render_template("loading.html")




@app.route("/account")
def account_page():
    """Account preferences page."""
    # pause account, change rec frequency, change email, pw, etc
    current_user = User.query.get(current_user_id)
    status = 0
    if current_user.paused == 1:
        status = "You paused your account on "+ str(current_user.paused_date)

    return render_template("account.html", User=current_user, status=status)



@app.route("/recommendations")
def recommendations():
    """List of all recommendations; allows users to leave feedback on recommendations."""

    current_user = User.query.get(1)

    query = Recommendation.query.filter(Recommendation.date_provided <= dt.datetime.now(), 
        Recommendation.userbook.has(user_id=current_user_id))

    recs_to_date=query.order_by(desc(Recommendation.date_provided)).all()

    if recs_to_date[0].date_provided.date() == dt.date.today():
        recs_to_show=recs_to_date[1:]
        today_rec = recs_to_date[0]
    else:
        recs_to_show=recs_to_date
        today_rec=False

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




#### APP MAINTENANCE ####
# need to send emails to all users at noon
# need to update database daily at midnight
# scheduler.start()




#### FUNCTION CALLS ####
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()

