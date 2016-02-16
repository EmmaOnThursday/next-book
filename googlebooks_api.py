import os
import requests
import pdb
from model import Book, Subject, BookSubject, connect_to_db, db
from server import app

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

def fetch_google_books_categories():
    """Retrieves Google Books categories for any new library books."""

    # get list of ISBNs for books that need subjects
    need_subjects = Book.query.filter(Book.get_subjects==1, Book.isbn!='0').all()
    # print len(need_subjects)

    subject_dict = {}
    googlebooks_count = 0

    for book in need_subjects:
        #get isbn & query google books; extract categories from response
        current_isbn = book.isbn
        book_data = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:%s&key=%s" % (current_isbn, GOOGLE_API_KEY)).json()
        
        if book_data.get('items'):
            googlebooks_count += 1 
            if book_data['items'][0]['volumeInfo'].get('categories', None):
                subjects = book_data['items'][0]['volumeInfo']['categories']
            
            # save categories in subject table; mark source as google-books
            # maybe make this its own function?
                for category in subjects:
                    category = category.lower()
                    print "category:", category, type(category)

                    is_subject = Subject.query.filter_by(subject=category).first()
                    if is_subject == None:
                        subject = Subject(subject=category, source='GoogleBooks')
                        db.session.add(subject)

                    # add each subject to a dictionary of bookID & list of subject
                    if subject_dict.get(book.book_id, None):
                        subject_dict[book.book_id].append(category)
                    else:
                        subject_dict[book.book_id] = [category]
                # book.get_subjects = 0
                # db.session.add(book)

    db.session.commit() 
    print googlebooks_count
    return subject_dict




def create_book_subjects(subject_dict):
    """Given a dictionary of book_ids & associated subjects, create BookSubjects."""

    # item is a book_id; values are lists of associated categories
    for item in subject_dict.keys():
        for category in subject_dict[item]:
            subject = Subject.query.filter(Subject.subject==category).first()
            is_booksubject = BookSubject.query.filter(BookSubject.book_id==item, BookSubject.subject_id==subject.subject_id).first()
            if is_booksubject == None:
                new_booksubject = BookSubject(subject_id=subject.subject_id, book_id=item)
            db.session.add(new_booksubject)

    db.session.commit()




# https://www.googleapis.com/books/v1/volumes?q=isbn:9780771068713
#  "The English Patient"

###################################
# FUNCTION CALLS

connect_to_db(app)

subject_dict = fetch_google_books_categories()

create_book_subjects(subject_dict)

