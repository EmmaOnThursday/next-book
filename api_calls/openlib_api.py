import os
import requests
import pdb
from model import Book, Subject, BookSubject, connect_to_db, db
from googlebooks_api import create_book_subjects



def fetch_openlib_subject_info():
    """Based on a book's ISBN or Goodreads ID, fetch subject info from OpenLib."""

    # get ISBNs of books that need subject info
    need_subjects = Book.query.filter(Book.get_subjects==1, Book.isbn!='0').all()
    print "need subjects for:", len(need_subjects)

    subject_dict = {}
    openlib_count = 0

    for book in need_subjects:
        current_isbn = book.isbn
        response = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:%s&format=json&jscmd=data" % (current_isbn))
        book_info = response.json()
        
        if book_info.keys():
            current_key = "ISBN:%s" % (current_isbn)
            if book_info[current_key].get('subjects', None):
                openlib_count += 1
                categories = book_info[current_key]['subjects']
                
                # save categories in subject table; mark source as google-books
                for category in categories:
                    category = category['name'].lower()
                    # print "category:", category, type(category)

                    is_subject = Subject.query.filter_by(subject=category).first()
                    if is_subject == None:
                        subject = Subject(subject=category, source='OpenLib')
                        db.session.add(subject)

                    if subject_dict.get(book.book_id, None):
                        subject_dict[book.book_id].append(category)
                    else:
                        subject_dict[book.book_id] = [category]
    print "retrieved subjects for:", openlib_count
    db.session.commit() 
    return subject_dict


###################################
# FUNCTION CALLS


# subject_items = fetch_openlib_subject_info()

# create_book_subjects(subject_items)




