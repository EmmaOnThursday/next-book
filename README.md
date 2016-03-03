# NextBook


Many avid readers suffer from Reading List Paralysis: when you finish a great book, it feels entirely impossible to select a new one.

NextBook prevents RLP before it starts by providing one tailored book recommendation per day - for anyone with a Goodreads account. 
When a user signs up, NextBook pulls their book ratings from the Goodreads API, then retrieves additional book data from the Google 
Books & OpenLibrary APIs. Multiple machine learning models are trained on each user's ratings; the most accurate model selects books 
to recommend from NextBook's library. Users are emailed one title per day, avoiding option overload. Feedback is collected on every
suggestion, so NextBook can tailor recommendations more effectively over time.
