#!/usr/bin/env python

import os
import unittest
import doctest
import requests
import xmltodict
from flask import Flask

import server
from server import app
from model import connect_to_db, db, example_data, User, UserBook, Recommendation, Book, Subject, BookSubject
from api_calls.googlebooks_api import fetch_google_books_categories, create_book_subjects
from api_calls.openlib_api import fetch_openlib_subject_info
from api_calls.new_user_api_calls import get_shelves, get_books_from_shelves, add_book_to_library, add_userbook_to_userbooks


goodreads_key=os.environ['GOODREADS_KEY']
goodreads_secret=os.environ['GOODREADS_SECRET']

googlebooks_key = os.environ['GOOGLE_API_KEY']


class NextBookTests(unittest.TestCase):
    """Test NextBook app."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Create secret key to access session
        app.secret_key = "ABC"

        # Connect to fake database
        connect_to_db(app, 'postgresql:///testdb')
        db.create_all()
        app.config['TESTING'] = True

        example_data()

    def test_user_table_in_db(self):
        user = User.query.get(1)
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.email, "emmaonthursday@gmail.com")

    def test_goodreads(self):
        """Test outputs of goodreads API."""
        user = User.query.get(1)
        gr_uid = user.goodreads_uid
        shelves = get_shelves(gr_uid)
        self.assertEqual(len(shelves), 3)

    def test_googlebooks(self):
        """Test outputs of googlebooks API.
        Example book is War & Peace."""
        current_isbn = 9780375760648
        book_data = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:%s&key=%s" % (current_isbn, googlebooks_key)).json()
        self.assertEqual(book_data.keys(), [u'totalItems', u'items', u'kind'])

    def test_openlibrary(self):
        """Test outputs of openlibrary API."""
        pass

    def test_create_recommendations(self):
        """Are recommendations created for a new user?"""
        pass

    def test_homepage(self):
        """Text NextBook homepage."""

        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)

    def test_rec_list_page(self):
        """Text NextBook recommendations list page."""

        result = self.client.get('/recommendations')
        self.assertEqual(result.status_code, 200)

    def test_rec_detail_page(self):
        """Text NextBook recommendation detail page."""

        result = self.client.get('/recommendations/1')
        self.assertEqual(result.status_code, 200)

    def tear_down(self):
        """Do this at the end of every test."""

        db.session.close()
        db.drop_all()


if __name__ == "__main__":
    import unittest
    unittest.main()
