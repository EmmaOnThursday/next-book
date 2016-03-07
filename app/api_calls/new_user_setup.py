import requests
import os

from ..model import Book, User, Recommendation, UserBook, connect_to_db, db

from new_user_api_calls import get_shelves, get_books_from_shelves, add_book_to_library, add_userbook_to_userbooks
from googlebooks_api import fetch_google_books_categories, create_book_subjects
from openlib_api import fetch_openlib_subject_info
from ..rec_creation_refactoring import *


GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
goodreads_key=os.environ['GOODREADS_KEY']
# goodreads_secret=os.environ['GOODREADS_SECRET']

gr_user_id = "16767050"

current_user_id = 1

def new_user_full_setup(gr_user_id, user_id, goodreads_key):
    shelves = get_shelves(gr_user_id, goodreads_key)
    book_list = get_books_from_shelves(shelves, goodreads_key)
    
    # check if book in library; if not, add to library
    add_book_to_library(book_list)
    
    # add book to UserBook table
    add_userbook_to_userbooks(book_list, gr_user_id)

    # get subjects for all new books
    # subject_dict = fetch_google_books_categories()
    subject_dict2 = fetch_openlib_subject_info()
    # print len(subject_dict)
    print len(subject_dict2)

    # create new book_subjects for new books
    # create_book_subjects(subject_dict)
    create_book_subjects(subject_dict2)

    # generate recommendations
    rated, to_rate = set_up_data(user_id)
    generate_new_user_predictions(rated, to_rate, user_id)

    return "New User Setup Complete"





