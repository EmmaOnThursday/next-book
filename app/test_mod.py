from model import User, db 

def test_function():
    # with app.app_context():   
    new_user = User(email="yoblin@gmail.com", 
        user_id=2, 
        f_name="Dan", l_name="Taylor", 
        goodreads_uid="738",
        paused=0,
        rec_frequency=1,
        sign_up_date="2015-01-01",
        password="yoblin")
    db.session.add(new_user)
    db.session.commit()
