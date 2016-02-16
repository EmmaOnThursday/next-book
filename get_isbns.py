import os
import requests
import pdb
from model import Book, Subject, BookSubject, connect_to_db, db
from server import app
from googlebooks_api import fetch_google_books_categories, create_book_subjects
from openlib_api import fetch_openlib_subject_info


ISBNDB_KEY = os.environ['ISBNDB_KEY']


def retrieve_isbns(titles):
    """Given a list of book titles, get ISBN numbers."""
    open "library_to_add.txt"

    for title in library_to_add:
        api_title = title with spaces replaced with "+"
        results = requests.get("http://isbndb.com/api/v2/json/%s/books?q=%s" % (ISBNDB_KEY, api_title)).json()
        first_book = results['data'][0]
        isbn = first_book['isbn13']
        author_raw = first_book['author_data'][0]['name'].split(',')
        author = " ".join(author_raw[::-1]).strip()
        
        # check if book already exists in my library (isbn, title+author)
        volume = Book.query.filter_by(isbn=isbn).first()
        if volume==None:
            volume = Book.query.filter(Book.title==title, Book.author==author).first()
        
        # if doesn't exist, create new book
        if volume==None:
            pages_raw = first_book['physical_description_text'].split(" ")
            pages = int(pages_raw[0])
            new_book = Book(isbn=isbn, 
                author=author, 
                title=title, 
                pages=pages, 
                publisher=str(first_book['publisher_name']), 
                language=str(first_book['language']),
                get_subjects=1)
            db.session.add(new_book)

    db.session.commit()
        



###################################
# FUNCTION CALLS

connect_to_db(app)

# get new books

retrieve_isbns("library_to_add.txt")

# get subjects for new books
subject_dict = fetch_google_books_categories()
subject_dict2 = fetch_openlib_subject_info()

# create new book_subjects for new books
create_book_subjects(subject_dict)
create_book_subjects(subject_dict2)






# "https://openlibrary.org/api/books?bibkeys=title:Catch-22&format=json&jscmd=data"


# 0679437223

# 9780679437222