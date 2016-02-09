from flask_sqlalchemy import SQLAlchemy
import pdb
import math 

db = SQLAlchemy()

#######################################################
#Model Definitions


# user class 
class User(db.Model):
    """NextBook users.

    Live in User table.
    """

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    goodreads_uid = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(15))
    rec_frequency = db.Column(db.Integer)
    sign_up_date = db.Column(db.Datetime)
    paused = db.Column(db.Boolean)
    paused_date = db.Column(db.Datetime)



# book class 
class Book(db.Model):
    """Books. 
    These are unique and live in the Library table.
    """

    __tablename__ = "library"

    book_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ISBN = db.Column(db.Integer)
    goodreads_bid = db.Column(db.Integer)
    openlib_bid = db.Column()
    google_bid = db.Column()
    title = db.Column(db.String(300))
    author = db.Column(db.String(300))
    pub_year = db.Column(db.Integer)
    preview = db.Column(db.String)
    pages = db.Column(db.Integer)
    subjects = ?????




class Recommendation(db.Model):
    """Recommendations provided by NextBook.
    Live in Recommendations table.
    """

    __tablename__ = "recommendations"

    rec_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    userbook_id = db.Column(db.Integer, db.ForeignKey('user_books.userbook_id'))
    date_created = db.Column()
    date_provided = db.Column()
    # response: read_now, read_later, already_read, reject
    response = db.Column(db.String(20))
 


class UserBook(db.Model):
    """Describes a user's relationship with a particular book.
    Live in UserBook table.
    """
    __tablename__ = "user_books"

    userbook_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('library.book_id'))
    gr_shelf_id = db.Column()
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


