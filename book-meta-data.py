import os
import requests
import xmltodict
import json
import pdb
from model import Book, User, Recommendation, UserBook, connect_to_db, db
from server import app

goodreads_key=os.environ['GOODREADS_KEY']
goodreads_secret=os.environ['GOODREADS_SECRET']


def fetch_book_metadata():
    """Based on a book's Goodreads ID, fetch metadata. 
    Calls OpenLib & GoogleBooks APIs.
    Savs data to library table."""

    # get original pub date, language from book.show method in GR API

    need_language = Book.query.filter(Book.language.is_(None)).all()   
    # language_count = 0

    for book in need_language:
        response = requests.get("https://www.goodreads.com/book/show/%s.json?key=%s" % (book.goodreads_bid, goodreads_key))
        parsed_response = json.loads(response.content)
        book_info = parsed_response['GoodreadsResponse']
        # pdb.set_trace()
        book.language = book_info['book']['language_code']
        # book.original_pub_year = int(book_info['book']['work']['original_publication_year']['#text'])
        # language_count += 1
    # return language_count

        # db.session.add(book)
    # db.session.flush()
###################################
# FUNCTION CALLS

connect_to_db(app)

books_updated = fetch_book_metadata()






# def fetch_subject_info():
#     """Based on a book's ISBN or Goodreads ID, fetch subject info. 
#     Calls OpenLib & GoogleBooks APIs."""

#     need_subjects = Book.query.filter(Book.get_subjects ==1).all()   

#     for book in need_subjects:


#     # for each book: 
#         # get ISBN
#         # OpenLib API call
#         # save subjects to subjects table
#         # get subject_ID
#         # save subject_ID & book_ID to book-subjects table
#         # wait 30 seconds
#     pass