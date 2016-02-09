from flask_sqlalchemy import SQLAlchemy
import pdb
import math 

db = SQLAlchemy()

#######################################################
#Model Definitions


class User(db.Model):
    """NextBook users."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    goodreads_uid = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(15), nullable=False)
    rec_frequency = db.Column(db.Integer, nullable=False, default=1)
    sign_up_date = db.Column(db.Datetime, nullable=False)
    paused = db.Column(db.Integer, nullable=False, default=0)
    paused_date = db.Column(db.Datetime)



class Book(db.Model):
    """Books. These are unique and live in the Library table."""

    __tablename__ = "library"

    book_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ISBN = db.Column(db.Integer)
    goodreads_bid = db.Column(db.Integer)
    openlib_bid = db.Column(db.String(20))
    google_bid = db.Column(db.String(20))
    title = db.Column(db.String(300))
    author = db.Column(db.String(300))
    pub_year = db.Column(db.Integer)
    preview = db.Column(db.String(200))
    pages = db.Column(db.Integer)
    publisher = db.Column(db.String(100))



class Recommendation(db.Model):
    """Recommendations provided by NextBook."""

    __tablename__ = "recommendations"

    rec_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    userbook_id = db.Column(db.Integer, db.ForeignKey('user_books.userbook_id'))
    date_created = db.Column(db.Datetime, nullable=False)
    date_provided = db.Column(db.Datetime)
    # response: read_now, read_later, already_read, reject
    response = db.Column(db.String(20))
 


class UserBook(db.Model):
    """Describes a user's relationship with a particular book."""
    __tablename__ = "user_books"

    userbook_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('library.book_id'))
    gr_shelf_id = db.Column(db.Integer)
    gr_shelf_name = db.Column(db.String(50))
    #status: read, currently_reading, want_to_read, rec_no_response, not_to_read
    status = db.Column(db.String(50)) 
    source = db.Column(db.String(50))
    rating = db.Column(db.Integer)


    book = db.relationship("Book",
            backref=db.backref("userbooks"))
    user = db.relationship("User", 
            backref=db.backref("userbooks"))
    recommendations = db.relationship("Recommendation", 
            backref=db.backref("userbook"))



class Subject(db.Model):
    """A subject that a book could talk about."""

    __tablename__ = "subjects"

    subject_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    # source = google_books, open_lib, possibly others?
    source = db.Column(db.String(25))


    books = db.relationship("Book", secondary = 'book_subjects', backref = "subjects")


class BookSubject(db.Model):
    """Association table to connect subjects & books.
    Tables connected are library & subjects"""

    __tablename__ = "book_subjects"

    booksubject_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('library.book_id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))



##############################################################################
# Helper functions

def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    # ALTER DATABASE NAME IF NECESSARY
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///nextbook'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


