import os
import requests
import json
import xmltodict
from goodreads import client

goodreads_key=os.environ['GOODREADS_KEY']
goodreads_secret=os.environ['GOODREADS_SECRET']

gc = client.GoodreadsClient(goodreads_key, goodreads_secret)


raw_shelf = requests.get('https://www.goodreads.com/review/list/16767050?format=xml&key=$%s&v=2&id=16767050&shelf=read&per_page=100' % (goodreads_key))

# this returns an XML; need to parse that?
parsed_shelf = xmltodict.parse(raw_shelf.content)
# print len(parsed_shelf.keys())
for x in parsed_shelf['GoodreadsResponse']['reviews']['review']:
    print x['book']['title'], "-", x['rating']



