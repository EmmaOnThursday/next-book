import os
import requests
import pdb
import sys
import xmltodict
from model import Book, Subject, BookSubject, connect_to_db, db
from server import app
from new_user_api_calls import get_shelves, get_books_from_shelves, add_book_to_library, fetch_book_data
from googlebooks_api import fetch_google_books_categories, create_book_subjects
from openlib_api import fetch_openlib_subject_info

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
goodreads_key=os.environ['GOODREADS_KEY']


def bulk_user_add(user_ids):

    for gr_user_id in user_ids:
        print gr_user_id  
        # get shelves
        shelves = get_shelves(gr_user_id)
        #get books from shelves
        book_list = get_books_from_shelves(shelves)
        # check if book in library; if not, add to library
        add_book_to_library(book_list)


connect_to_db(app)

bulk_user_add(user_ids)

fetch_book_data()

subject_dict = fetch_google_books_categories()
subject_dict2 = fetch_openlib_subject_info()

create_book_subjects(subject_dict)
create_book_subjects(subject_dict2)