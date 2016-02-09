import os
import requests
import json
import xmltodict
from goodreads import client

goodreads_key=os.environ['GOODREADS_KEY']
goodreads_secret=os.environ['GOODREADS_SECRET']

# gc = client.GoodreadsClient(goodreads_key, goodreads_secret)
# get user id

user_id = "16767050"

# get user info
user = requests.get('https://www.goodreads.com/user/show.xml?key=$%s&v=2&id=%s' % (goodreads_key, user_id))
# this returns an XML; now we parse:
user_info = xmltodict.parse(user.content)

shelves = {}
# extract user shelves: name, id, book count; eventually this should save to DB
for user_shelf in user_info['GoodreadsResponse']['user']['user_shelves']['user_shelf']:
    shelves[user_shelf['name']] = {'id': user_shelf['id']['#text'], 'item_count':user_shelf['book_count']['#text']}

# initialize user shelf dictionary
all_user_books = {}


# For each shelf: get book info name, author, goodreads ID, ISBN13, publish year, user rating
for shelf in shelves.keys():
    # figure out how many pages of 200 books per page are needed for each shelf
    if int(shelves[shelf]['item_count']) < 201:
        per_page = int(shelves[shelf]['item_count'])
        pages = 1
    else:
        per_page = 200
        pages = (int(shelves[shelf]['item_count'])/200) + 1

    books = []
    for page_num in range(1,pages+1):
        shelf_response = requests.get('https://www.goodreads.com/review/list.xml?key=$%s&v=2&id=%s&shelf=%s&per_page=%d&page=%d' % (goodreads_key, user_id, shelf, per_page, page_num))
        parsed_shelf = xmltodict.parse(shelf_response.content)
        for book in parsed_shelf['GoodreadsResponse']['reviews']['review']:
            books.append(book['book']['title'])
        # print shelf, page_num, len(books)
    all_user_books[shelf] = books
    # print shelf, len(books)

for key in all_user_books.keys():
    print key, len(all_user_books[key])



