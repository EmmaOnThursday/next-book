
import random
import datetime as dt
from server import app
from model import connect_to_db, db, Book, User, Recommendation, Subject, UserBook, BookSubject



def generate_recommendation_delivery_dates(i):
    active_users = User.query.filter(User.paused==0).all()
    # print len(active_users)

    for user in active_users:
        undelivered_recs = Recommendation.query.filter(Recommendation.userbook.has(UserBook.user_id==user.user_id), 
            Recommendation.date_provided == None).all()
        today = random.choice(undelivered_recs)
        today.date_provided = dt.datetime(2016, 3, i)
        db.session.add(today)

    db.session.commit()



###### FUNCTION CALLS ###### 
connect_to_db(app)

for i in range(1,2):
    generate_recommendation_delivery_dates(i)