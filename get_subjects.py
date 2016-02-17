import os
import requests
import pdb
import sys
import xmltodict
from model import Book, Subject, BookSubject, connect_to_db, db
from server import app
from googlebooks_api import fetch_google_books_categories, create_book_subjects
from openlib_api import fetch_openlib_subject_info

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']


# get subjects for new books
subject_dict = fetch_google_books_categories()
subject_dict2 = fetch_openlib_subject_info()

# create new book_subjects for new books
create_book_subjects(subject_dict)
create_book_subjects(subject_dict2)