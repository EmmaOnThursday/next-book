import os
import requests
import xmltodict
import pdb
from model import Book, User, Recommendation, UserBook, connect_to_db, db


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
    """Takes in dictionary of user's shelves; returns list of all books on shelves.
    Return list: books stored in tuples: (shelf name, book info)."""

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



##### ADD BOOK ####

def add_book_to_library(book_list):
    """Adds book to the library table if it does not already exist."""
    for item in book_list:
        book = item[1]
        book_info = book['book']
        current_isbn = book_info['isbn13']
        current_gr_bid = book_info['id']['#text']
        # pdb.set_trace()

        # tries to instantiate a book
        this_book = db.session.query(Book).filter_by(goodreads_bid = current_gr_bid).first()
        
        # if it fails, tries again with ISBN
        if not this_book:
            if len(current_isbn) == 13:
                this_book = db.session.query(Book).filter_by(isbn = current_isbn).first()
            else:
                current_isbn = "0"

        # if that fails, create a new book
        if not this_book:
            newbook = Book(title = book_info['title'], 
                            goodreads_bid = current_gr_bid,
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


###### GET ADDITIONAL BOOK METADATA ######
def fetch_book_data():
    """Based on book's Goodreads ID, fetch language & original publication year.
    Uses GR method book.show; saves data to library table."""

    to_update = Book.query.filter((Book.language.is_(None)) | (Book.original_pub_year.is_(None))).all()   

    # for book in need_language:
    for book in to_update:
        response = requests.get("https://www.goodreads.com/book/show/%s?key=%s&format=xml" % (book.goodreads_bid, goodreads_key))
        parsed_response = xmltodict.parse(response.content)
        book_info = parsed_response['GoodreadsResponse']
        book.original_pub_year = int(book_info['book']['work']['original_publication_year']['#text'])
        book.language = book_info['book']['language_code']
        db.session.add(book)

    db.session.commit()




###### ADD USERBOOK ######
def add_userbook_to_userbooks(book_list, gr_user_id):
    """Add a new userbook to the userbooks table."""
    
    current_user = User.query.filter_by(goodreads_uid=gr_user_id).one()

    for item in book_list:
        book = item[1] 
        shelf = item[0]
        book_info = book['book']
        gr_bid = int(book_info['id']['#text'])
        current_isbn = book_info['isbn13']

        #set status
        if shelf in ['read', 'currently-reading']:
            status = 'read'
        elif shelf == 'to-read':
            status = 'want-to-read'
        else:
            status = None

        # try to get book from library with goodreads ID
        library_record = Book.query.filter_by(goodreads_bid=gr_bid).first()

        # if book does not exist w/ goodreads id, try to get it with ISBN
        if not library_record:
            if len(current_isbn) == 13:
                library_record = db.session.query(Book).filter_by(isbn=current_isbn).first()
        if not library_record:
            print "Failed to record user rating for ", book_list[1][1]['book']['title'], "user = ", current_user.email
        else:
            new_volume = UserBook.query.filter(UserBook.user_id==current_user.user_id, UserBook.book_id == library_record.book_id).first()

            if not new_volume:
                if book['rating'] != 0:
                    status = 'read'
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


# shelves = get_shelves(gr_user_id)

# book_list = get_books_from_shelves(shelves)

# # check if book in library; if not, add to library
# add_book_to_library(book_list)

# # add book to UserBook table
# add_userbook_to_userbooks(book_list, gr_user_id)


