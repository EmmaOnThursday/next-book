""" Server for NextBook """

import datetime as dt
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, url_for
# from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Book, User, Recommendation, Subject, UserBook, BookSubject



app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Prevents undefined variables in Jinja from failing silently.
# Instead of that horrible thing, raies an error.
app.jinja_env.undefined = StrictUndefined

current_user_id = 1
today = dt.datetime.now()

@app.route("/")
def index():
    """Landing page; includes login.""" 

    return render_template("home.html")


@app.route("/sign-up")
def sign_up():
    """For new users only: sign-up page."""  

    return render_template("sign-up.html")


@app.route("/recs-loading")
def loading():
    """For new users only: waiting for recommendations to generate."""
    # cute gif here.

    return render_template("loading.html")


@app.route("/account")
def account_page():
    """Account preferences page."""
    # pause account
    # change rec frequency
    # change email, pw, etc
    current_user = User.query.get(current_user_id)
    status = 0
    if current_user.paused == 1:
        status = "You paused your account on "+current_user.paused_date

    return render_template("account.html", User=current_user, status=status)


# @app.route("/todays-rec")
# def  
#     """Landing page after login: displays today's recommendation."""
#     # provides today's rec and... ?


@app.route("/recommendations")
def recommendations():
    """List of all previous recommendations."""
    
    # show_recs = Recommendation.query.filter(Recommendation.user_id == current_user_id, 
    #     Recommendation.date_provided < today).all()

    # link to each rec preview page
    # allows users to provide feedback on rec, & view/change previous feedback
    show_recs = ['War & Peace', 'Little Women']

    return render_template("recommendation-list.html", show_recs=show_recs)


@app.route("/recommendations/<int:rec_id>")
def rec_details():
    """Provides details on each specific recommendation."""
    # provides preview of book text
    # gives details of book (author, links to other pages, etc)
    # allows users to provide feedback on rec, & view/change previous feedback

    return render_template("recommendation-detail.html")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run()

