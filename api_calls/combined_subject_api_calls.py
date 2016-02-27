import os
import requests
import pdb
from model import Book, Subject, BookSubject, connect_to_db, db
from server import app




def category_handler(subject_dict, book_object, subject_list, source):
    """Takes in categories returned from OpenLib or Google Books. 
    Normalizes category names & saves subjects to dictionary."""

    for category in subject_list:
        category = category.lower()

        delimiters = [" in fiction", "(", ", ", "=", "/"]
        for sep in delimiters:
            keep, delim, delete = category.partition(sep)
            category = keep

        is_subject = Subject.query.filter_by(subject=category).first()
        if is_subject == None:
            new_subject = Subject(subject=category, source=source)
            db.session.add(new_subject)

        if subject_dict.get(book_object.book_id, None):
            subject_dict[book_object.book_id].add(category)
        else:
            subject_dict[book_object.book_id] = {category}

    return subject_dict


GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']


# Maybe call this whole function once per new book in library, rather than as a big batch?
def fetch_subjects():
    """Retrieves Google Books categories for any new library books."""

    # get list of ISBNs for books that need subjects
    need_subjects = Book.query.filter(Book.get_subjects==1, Book.isbn!='0').all()
    print "Need subjects for x books:", len(need_subjects)
    subject_dict = {}
    updated_books_count = 0

    for book in need_subjects:
        #get isbn
        if len(book.isbn) == 13:
            current_isbn = book.isbn

            # query GoogleBooks API
            book_data = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:%s&key=%s" % (current_isbn, GOOGLE_API_KEY)).json()
            source = 'GoogleBooks'

            if book_data.get('items'):
                updated_books_count += 1
                if book_data['items'][0]['volumeInfo'].get('categories', None):
                    subjects = book_data['items'][0]['volumeInfo']['categories']
                    # print subjects
                    subject_dict = category_handler(subject_dict, book, subjects, source)

            # query OpenLibrary & get subject info out of response
            book_info = requests.get("https://openlibrary.org/api/books?bibkeys=ISBN:%s&format=json&jscmd=data" % (current_isbn)).json()
            source = "OpenLib"
            
            if book_info.keys():
                updated_books_count += 1
                current_key = "ISBN:%s" % (current_isbn)
                if book_info[current_key].get('subjects'):
                    categories = book_info[current_key]['subjects']
                    subjects = []
                    for category in categories:
                        subjects.append(category['name'])
                    subject_dict = category_handler(subject_dict, book, subjects, source)    

            found_subjects = subject_dict.get(book.book_id)
            if found_subjects:
                subj_count = len(found_subjects)
            else:
                subj_count=0
            print "Found", subj_count, "subjects for", book.title

    print "Found subjects for x books:", updated_books_count
    db.session.commit() 
    return subject_dict



def create_book_subjects(subject_dict):
    """Given a dictionary of book_ids & associated subjects, create BookSubjects."""

    # item is a book_id; values are sets of associated categories
    for item in subject_dict.keys():
        for subject in subject_dict[item]:
            subject = Subject.query.filter(Subject.subject==subject).first()
            is_booksubject = BookSubject.query.filter(BookSubject.book_id==item, BookSubject.subject_id==subject.subject_id).first()
            if is_booksubject == None:
                new_booksubject = BookSubject(subject_id=subject.subject_id, book_id=item)
                db.session.add(new_booksubject)

    db.session.commit()



###################################
# FUNCTION CALLS

connect_to_db(app)

subject_dict = fetch_subjects()

create_book_subjects(subject_dict)
