import os
import requests
from ..model import Book, Subject, BookSubject, connect_to_db, db

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# Maybe call this whole function once per new book in library, rather than as a big batch?

def fetch_google_books_categories():
    """Retrieves Google Books categories for any new library books."""

    # get list of ISBNs for books that need subjects
    # how do I make sure this is retrieving all data now, instead of being lazy about it?
    need_subjects = Book.query.filter(Book.get_subjects==1, Book.isbn!='0').all()
    print "Need subjects for x books:", len(need_subjects)
    subject_dict = {}
    googlebooks_count = 0

    for book in need_subjects:
        #get isbn & query google books; extract categories from response
        if len(book.isbn) == 13:
            current_isbn = book.isbn
            book_data = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:%s&key=%s" % (current_isbn, GOOGLE_API_KEY)).json()
            source = 'GoogleBooks'
            if book_data.get('items'):
                googlebooks_count += 1 
                
                # if response contains categories, save them to subjects table
                if book_data['items'][0]['volumeInfo'].get('categories', None):
                    subjects = book_data['items'][0]['volumeInfo']['categories']
                    # save categories in subject table; mark source as google-books
                    for category in subjects:
                        category = category.lower()
                        is_subject = Subject.query.filter_by(subject=category).first()
                        if is_subject == None:
                            subject = Subject(subject=category, source='GoogleBooks')
                            db.session.add(subject)
                    # add each subject to a dictionary of bookID & list of subject

                    # create dictionary to use to populate book_subjects table
                    if subject_dict.get(book.book_id):
                        subject_dict[book.book_id].append(category)
                    else:
                        subject_dict[book.book_id] = [category]

    print "Found subjects for x books:", googlebooks_count
    db.session.commit() 
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
    return


