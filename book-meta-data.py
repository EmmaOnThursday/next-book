import os
import requests
import xmltodict
import pdb
from model import Book, User, Recommendation, UserBook, connect_to_db, db
from server import app

goodreads_key=os.environ['GOODREADS_KEY']
goodreads_secret=os.environ['GOODREADS_SECRET']


def fetch_book_metadata():
    """Based on a book's Goodreads ID, fetch metadata. 
    Calls OpenLib & GoogleBooks APIs.
    Savs data to library table."""

    need_language = Book.query.filter(Book.language).all()   

    for book in need_subjects:




def fetch_subject_info():
    """Based on a book's ISBN or Goodreads ID, fetch subject info. 
    Calls OpenLib & GoogleBooks APIs."""

    need_subjects = Book.query.filter(Book.get_subjects ==1).all()   

    for book in need_subjects:


    # for each book: 
        # get ISBN
        # OpenLib API call
        # save subjects to subjects table
        # get subject_ID
        # save subject_ID & book_ID to book-subjects table
        # wait 30 seconds
        # get original pub date, language from book.show method in GR API
    pass