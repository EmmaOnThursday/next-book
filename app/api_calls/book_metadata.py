import os
import requests
import xmltodict
import pdb
from model import Book, User, Recommendation, UserBook, connect_to_db, db

goodreads_key=os.environ['GOODREADS_KEY']
# goodreads_secret=os.environ['GOODREADS_SECRET']


def fetch_book_data():
    """Based on book's Goodreads ID, fetch language & original publication year.
    Uses GR method book.show; saves data to library table."""

    to_update = Book.query.filter((Book.language.is_(None)) | (Book.original_pub_year.is_(None))).all()   
    print len(to_update)

    # for book in need_language:
    for book in to_update:
        response = requests.get("https://www.goodreads.com/book/show/%s?key=%s&format=xml" % (book.goodreads_bid, goodreads_key))
        parsed_response = xmltodict.parse(response.content)
        book_info = parsed_response['GoodreadsResponse']
        # pdb.set_trace()
        book.original_pub_year = int(book_info['book']['work']['original_publication_year']['#text'])
        book.language = book_info['book']['language_code']
        db.session.add(book)

    db.session.commit()




###################################
# FUNCTION CALLS

# connect_to_db(app)

# fetch_book_metadata()






