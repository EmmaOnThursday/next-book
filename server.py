""" Server for NextBook """

import datetime as dt
from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Book, User, Recommendation, Subject, UserBook, BookSubject
from sqlalchemy import desc


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


@app.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    """For new users only: sign-up page."""  

    # if form has been submitted...
    if request.method == 'POST':
        #save all variables from form
        email = request.form.get('email')
        password  = request.form.get('password')
        goodreads_uid = int(request.form.get('goodreads_uid'))
        rec_frequency = int(request.form.get('rec_frequency'))

        # try to instantiate user based on email from form
        user = User.query.filter(User.email == email).all()

        # if user already in DB, redirect to login page
        if user != []:
            flash("Looks like you've already signed up! Please log in.")
            return redirect(url_for('login'))
        
        # if user does not exist, create & commit to DB
        else:
            new_user = User(email=email, password=password, 
                goodreads_uid=goodreads_uid, rec_frequency=rec_frequency,
                sign_up_date=dt.datetime.now(), paused=0)
            print new_user
            # db.session.add(new_user)
            # db.session.commit()
            flash("Welcome to NextBook!")
            return redirect(url_for('loading'))

#### NEED TO CALL ALL NEW USER FUNCTIONS HERE ####

    return render_template('sign-up.html')





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
        status = "You paused your account on "+current_user.paused_date

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
    # gives details of book (author, links to other pages, etc) & link to book/book preview
    # allows users to provide feedback on rec, & view/change previous feedback

    current_rec = Recommendation.query.get(rec_id)

    return render_template("recommendation-detail.html", rec=current_rec)


@app.route("/recommendations/<int:rec_id>/user-feedback", methods=['POST'])
def record_user_feedback(rec_id):
    """Takes in user feedback from recommendations & saves to Postgres."""

    print "############# got to route"
    response = request.form.get('response')
    print response
    rec_id = request.form.get('rec_id')
    print rec_id
    current_rec = Recommendation.query.get(rec_id)
    current_rec.response = response # get response from user input

    db.session.add(current_rec)
    db.session.commit()

    button_to_color = {'rec_id': rec_id, 'button': response}

    return jsonify(button_to_color)




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()

