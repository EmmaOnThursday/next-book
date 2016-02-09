""" Server for NextBook """


from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Prevents undefined variables in Jinja from failing silently.
# Instead of that horrible thing, raies an error.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
    """Landing page; includes login."""


@app.route("/sign-up")
    """For new users only: sign-up page."""


@app.route("/recs-loading")
    """For new users only: waiting for recommendations to generate."""
    # cute gif here.


@app.route("/todays-rec")
    """Landing page after login: displays today's recommendation."""
    # provides today's rec and... ?


@app.route("/recommendations")
    """List of all previous recommendations."""
    # link to each rec preview page
    # allows users to provide feedback on rec, & view/change previous feedback


@app.route("/preview")
    """Provides details on each specific recommendation."""
    # provides preview of book text
    # gives details of book (author, links to other pages, etc)
    # allows users to provide feedback on rec, & view/change previous feedback


