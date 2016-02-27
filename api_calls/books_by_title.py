import os
import requests
import pdb
import sys
import xmltodict
from model import Book, connect_to_db, db
from server import app
from googlebooks_api import fetch_google_books_categories, create_book_subjects
from openlib_api import fetch_openlib_subject_info


goodreads_key=os.environ['GOODREADS_KEY']
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']


def book_data_by_title(titles_file):
    """Given a list of book titles, instantiate book objects via Goodreads API."""
    
    titles = open(titles_file)
    library_to_add = []
    for line in titles:
        line = line.strip()
        library_to_add.append(line)
    titles.close()


    for title in library_to_add:
        api_title = title.replace(" ", "+")
        print api_title
        # using Goodreads book.title method
        results = requests.get("https://www.goodreads.com/book/title.xml?key=%s&title=%s" % (goodreads_key, api_title))
        results = xmltodict.parse(results.content)
        if results.get('GoodreadsResponse'):
            book_info = results['GoodreadsResponse']['book']
            isbn = book_info['isbn13']
            author_info = book_info['authors']['author']
            if isinstance(author_info, dict):
                author = author_info['name']
            if isinstance(author_info, list):
                author=author_info[0]['name']
            goodreads_id = book_info['id']

            # check if book already exists in my library (isbn, title+author)
            volume = Book.query.filter((Book.isbn==isbn) | (Book.goodreads_bid==goodreads_id)).first()
            if volume==None:
                volume = Book.query.filter(Book.title==title, Book.author==author).first()
            
            # if doesn't exist, create new book
            if volume==None:
                # checks if goodreads has original publication year available; if not, sets to None
                year = book_info['work']['original_publication_year'].get('#text')
                if year:
                    year = int(year)
                
                pub_year = book_info['publication_year']
                if pub_year:
                    pub_year = int(pub_year)

                pages = book_info['num_pages']
                if pages:
                    pages = int(pages)

                new_book = Book(isbn=isbn, 
                    author=author,
                    goodreads_bid=int(goodreads_id),
                    title=title, 
                    pages=pages,
                    pub_year=pub_year,
                    publisher=book_info['publisher'],
                    language=book_info['language_code'],
                    original_pub_year=year,      
                    goodreads_url=book_info['url'],
                    img_url=book_info['image_url'],
                    get_subjects=1)
                db.session.add(new_book)

    db.session.commit()
        


###################################
# FUNCTION CALLS

connect_to_db(app)

# get new books
titles_file = sys.argv[1]
book_data_by_title(titles_file)

subject_dict = fetch_google_books_categories()
subject_dict2 = fetch_openlib_subject_info()

create_book_subjects(subject_dict)
create_book_subjects(subject_dict2)


