import os
import requests
import xmltodict
import pdb
from model import Book, User, Recommendation, UserBook, connect_to_db, db
from server import app

goodreads_key=os.environ['GOODREADS_KEY']
goodreads_secret=os.environ['GOODREADS_SECRET']

# get user id (this will be via OAuth probably)
gr_user_id = "16767050"


def get_shelves(gr_user_id):
    """Pulls user's shelves out of their user info."""
    user = requests.get('https://www.goodreads.com/user/show.xml?key=$%s&v=2&id=%s' % (goodreads_key, gr_user_id))
    user_info = xmltodict.parse(user.content)
    # initialize user shelf dictionary
    shelves = {}
    # extract user shelves: name, id, book count; eventually this should save to DB
    for user_shelf in user_info['GoodreadsResponse']['user']['user_shelves']['user_shelf']:
        shelf_name = user_shelf['name']
        shelf_id = user_shelf['id']['#text']
        num_of_books = int(user_shelf['book_count']['#text'])
        num_pages = (num_of_books/200) + 1
        shelves[shelf_name] = {'id': shelf_id, 'item_count': num_of_books, 'pages': num_pages}

    return shelves



def get_books_from_shelves(shelves):
    """Takes in dictionary of user's shelves; returns list of all books on shelves."""

    all_books = []

    for shelf in shelves.keys():
        pages = shelves[shelf]['pages']
        for page in range(1,pages+1):
            shelf_response = requests.get('https://www.goodreads.com/review/list.xml?key=$%s&v=2&id=%s&shelf=%s&per_page=200&page=%d' 
                                            % (goodreads_key, gr_user_id, shelf, page))
            parsed_shelf = xmltodict.parse(shelf_response.content)
            for book in parsed_shelf['GoodreadsResponse']['reviews']['review']:
                all_books.append((shelf, book))
    return all_books



def add_book_to_library(book_list):
    """Adds book to the library table if it does not already exist."""
    for item in book_list:
        book = item[1]
        book_info = book['book']
        current_isbn = book_info['isbn13']
        current_gr_bid = book['id']

        # does this goodreads ID exist in my db?
            # yes: stop right there
            # no: does this book have an ISBN?
                # yes: does that ISBN exist in my DB?
                    # yes: stop right there
                    # no: create a book
                # no: save book with ISBN of 0

        # tries to instantiate a book
        this_book = db.session.query(Book).filter_by(goodreads_bid = current_gr_bid).first()
        
        # if it fails, tries again with ISBN
        if not this_book:
            if len(current_isbn) == 13:
                this_book = db.session.query(Book).filter_by(isbn = current_isbn).first()
            else:
                current_isbn = "0"
        
        # if this_book:
            # print "book exists at id ", this_book.book_id

        # if that fails, create a new book
        if not this_book:
            newbook = Book(title = book_info['title'], 
                            goodreads_bid = book['id'],
                            author = book_info['authors']['author']['name'],
                            isbn = current_isbn,
                            pub_year = book_info['publication_year'],
                            pages = book_info['num_pages'],
                            publisher = book_info['publisher'],
                            img_url = book_info['image_url'],
                            goodreads_url = book_info['link'],
                            get_subjects = 1)
            db.session.add(newbook)

    db.session.commit()
            # print "new book created at id ", newbook.book_id


def add_userbook_to_userbooks(book_list, gr_user_id):
    """Add a new userbook to the userbooks table."""
    
    current_user = User.query.filter_by(goodreads_uid=gr_user_id).one()
    print len(book_list)

    for item in book_list:
        # pdb.set_trace()
        book = item[1] 
        shelf = item[0]
        book_info = book['book']
        gr_bid = int(book['id'])
        print gr_bid, "type= ", type(gr_bid)
        current_isbn = book_info['isbn13']

        #set status
        if shelf in ['read', 'currently-reading']:
            status = 'read'
        elif shelf == 'to-read':
            status = 'want-to-read'
        else:
            status = None

        # try to get book from library with goodreads ID
        library_record = Book.query.filter_by(goodreads_bid = gr_bid).first()
        print type(library_record)

        # if book does not exist w/ goodreads id, try to get it with ISBN
        if not library_record:
            print "reached line 138"
            if len(current_isbn) == 13:
                library_record = db.session.query(Book).filter_by(isbn = current_isbn).first()
                print "reached line 139"
        if not library_record:
            print "Failed to record user rating for ", book_list[1][1]['book']['title'], "user = ", current_user.email
        
        new_volume = UserBook.query.filter(UserBook.user_id==current_user.user_id, 
                                            UserBook.book_id == library_record.book_id).first()
        
        if new_volume: 
            print "have this record already at userbook_id", new_volume.userbook_id

        if not new_volume:
            new_userbook = UserBook(user_id = current_user.user_id,
                                    book_id = library_record.book_id,
                                    gr_shelf_name = shelf, 
                                    gr_shelf_id = shelves[shelf]['id'],
                                    source = "goodreads",
                                    status = status,
                                    rating = book['rating'])
            db.session.add(new_userbook)
            print "created new record at userbook_id", new_userbook.userbook_id
    db.session.commit()



###################################
# FUNCTION CALLS

connect_to_db(app)

shelves = get_shelves(gr_user_id)

book_list = get_books_from_shelves(shelves)

# check if book in library; if not, add to library
add_book_to_library(book_list)

# add book to UserBook table
add_userbook_to_userbooks(book_list, gr_user_id)


######################################################################
# GET SUBJECT BOOK INFO
# for each book in library:
    # if has get_subjects = True:
    # go out and get book data from OpenLib
    # extract subjects
        # for each subject
            # if not in subjects, add to subjects
            # add to subject-book with book id

    # go get book info from GoogleBooks
    # extract categories
        # for each category
            # if not in subjects, add to subjects
            # add to subject-book with book id


