# set a rec as deliver_today every single day;
# run this script via a cronjob at 12:01 PST every day ????
# or look into celery; is this a better solution?

import random
import datetime as dt
from server import app
from model import connect_to_db, db, Book, User, Recommendation, Subject, UserBook, BookSubject

def generate_recommendation_delivery_dates():
    active_users = User.query.filter(User.paused==0).all()
    # print len(active_users)

    for user in active_users:
        undelivered_recs = Recommendation.query.filter(Recommendation.userbook.has(UserBook.user_id==user.user_id), 
            Recommendation.date_provided == None).all()
        # print len(undelivered_recs)
        today = random.choice(undelivered_recs)
        today.date_provided = dt.date.today()
        print today.rec_id
        db.session.add(today)

    db.session.commit()



###### FUNCTION CALLS ###### 
connect_to_db(app)
generate_recommendation_delivery_dates()