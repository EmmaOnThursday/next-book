import pdb
import math
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """NextBook users."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    f_name = db.Column(db.String(30), nullable=True)
    l_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    goodreads_uid = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(15), nullable=False)
    rec_frequency = db.Column(db.Integer, nullable=False, default=1)
    sign_up_date = db.Column(db.DateTime, nullable=False)
    paused = db.Column(db.Integer, nullable=False, default=0)
    paused_date = db.Column(db.DateTime, nullable=True)


class Book(db.Model):
    """Books. These are unique and live in the Library table."""

    __tablename__ = "library"

    book_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    isbn = db.Column(db.String(13))
    goodreads_bid = db.Column(db.Integer)
    openlib_bid = db.Column(db.String(20))
    google_bid = db.Column(db.String(20))
    title = db.Column(db.String(300))
    author = db.Column(db.String(300))
    pub_year = db.Column(db.Integer)
    original_pub_year = db.Column(db.Integer)
    preview = db.Column(db.String(200))
    pages = db.Column(db.Integer)
    publisher = db.Column(db.String(100))
    language = db.Column(db.String(15))
    img_url = db.Column(db.String(300))
    goodreads_url = db.Column(db.String(300))
    get_subjects = db.Column(db.Integer, default = 0)


class Recommendation(db.Model):
    """Recommendations provided by NextBook."""

    __tablename__ = "recommendations"

    rec_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    userbook_id = db.Column(db.Integer, db.ForeignKey('user_books.userbook_id'))
    date_created = db.Column(db.DateTime, nullable=False)
    date_provided = db.Column(db.DateTime, nullable=True)
    # response: read_now, read_later, already_read, reject
    response = db.Column(db.String(20), nullable=True)



class UserBook(db.Model):
    """Describes a user's relationship with a particular book."""
    __tablename__ = "user_books"

    userbook_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('library.book_id'))
    gr_shelf_id = db.Column(db.Integer, nullable=True)
    gr_shelf_name = db.Column(db.String(50), nullable=True)
    #status: read, currently_reading, want_to_read, rec_no_response, not_to_read
    status = db.Column(db.String(50), nullable=False)
    source = db.Column(db.String(50), nullable=True)
    rating = db.Column(db.Integer, nullable=True)


    book = db.relationship("Book",
            backref = db.backref("userbooks"))
    user = db.relationship("User",
            backref = db.backref("userbooks"))
    recommendations = db.relationship("Recommendation",
            backref = db.backref("userbook"))



class Subject(db.Model):
    """A subject that a book could talk about."""

    __tablename__ = "subjects"

    subject_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True)
    subject = db.Column(db.String(100),
                        nullable=False)
    # source = google_books, open_lib, possibly others?
    source = db.Column(db.String(25), nullable=False)

    books = db.relationship("Book",
            secondary = 'book_subjects',
            backref = "subjects")


class BookSubject(db.Model):
    """Association table to connect subjects & books.
    Tables connected are library & subjects"""

    __tablename__ = "book_subjects"

    booksubject_id = db.Column(db.Integer,
                            autoincrement=True,
                            primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('library.book_id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'))



def init_app():
    from flask import Flask
    app = Flask(__name__)
    connect_to_db(app)
    print "Connected to DB."


def connect_to_db(app, db_uri='postgres:///nextbook'):
    """Connect the database to our Flask app."""

    # Configure to use PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all
    return app


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.
    init_app()


##############################################################################
# Example data creation

def example_data():

    Recommendation.query.delete()
    UserBook.query.delete()
    User.query.delete()
    Book.query.delete()

    new_user = User(user_id = 1,
                    f_name = "Test",
                    l_name = "User",
                    email = "emmaonthursday@gmail.com",
                    password = "Goodreads",
                    goodreads_uid = 16767050,
                    rec_frequency = 1,
                    sign_up_date = "01-01-2016",
                    paused = 0)

    new_book = Book(book_id = 1,
                    isbn = "9780375760648",
                    title = "War and Peace",
                    author = "Leo Tolstoy",
                    goodreads_bid = 18243)

    new_userbook = UserBook(userbook_id = 1,
                            book_id = 1,
                            user_id = 1,
                            status = "read",
                            source = "nextbook",
                            rating = "5")

    new_recommendation = Recommendation(rec_id = 1,
                        userbook_id = 1,
                        date_created = "02-01-2016",
                        date_provided = "02-29-2016",
                        response = "read_now")

    db.session.add_all([new_book, new_user, new_userbook, new_recommendation])

    db.session.commit()
