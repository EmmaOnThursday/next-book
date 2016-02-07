import os
import requests
import json
import xmltodict
from goodreads import client

goodreads_key=os.environ['GOODREADS_KEY']
goodreads_secret=os.environ['GOODREADS_SECRET']

gc = client.GoodreadsClient(goodreads_key, goodreads_secret)

# url = "https://www.goodreads.com/search.xml?key=$"+goodreads_key+"&q=The+Wind+In+The+Willows"

# result = os.popen("curl " + url).read()

result = requests.get('https://www.goodreads.com/search.xml?key=$%s&q=The+Wind+In+The+Willows' % (goodreads_key) )
print result.status_code
content =  result.content
parsed = xmltodict.parse(content)
# for item in parsed.keys():
#     title = parsed[item].get('title')
#     print title

print len(parsed.keys())