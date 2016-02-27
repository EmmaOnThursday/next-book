from celery import Celery

# this will probably work; if not, go back to celery config docs
BROKER_URL = 'sqla+postgresql:///nextbook'

app = Celery('celery_app', broker=BROKER_URL)

@app.task
def add_recommendation_provided_date():
    """Adds date_provided to one rec per user in database."""
    print "this is the date_provided function"



@app.task
def send_recommendation_email():
    """Send recommendation email to each active user."""    
    print "this is the date_provided function"



