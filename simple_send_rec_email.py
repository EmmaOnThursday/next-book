# from celery import Celery
# from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
# from flask_debugtoolbar import DebugToolbarExtension

from server import app

import datetime as dt

from model import Book, User, Recommendation, UserBook, connect_to_db, db

import smtplib
import os

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


def send_recommendation_email():
    """Send a recommendation email to each active user with today's book."""
    fromaddr = os.environ.get("NEXTBOOK_GMAIL")
    username = fromaddr
    password = os.environ.get("NEXTBOOK_GMAIL_PW")  
    
    active_users = User.query.filter(User.paused==0).all()
    if active_users:
        for user in active_users:
            today_rec = Recommendation.query.filter(
                Recommendation.userbook.has(UserBook.user_id==user.user_id),
                Recommendation.date_provided==dt.date.today()).first()
            rec_title = today_rec.userbook.book.title
            rec_link = today_rec.userbook.book.goodreads_url
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = user.email
            msg['Subject'] = "Today\'s Recommendation!"
            body = "Here's today's recommendation!\n"+rec_title+": "+rec_link+"\nWith love from NextBook"
            msg.attach(MIMEText(body, 'plain'))

            # The actual mail send
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.login(username,password)
            text = msg.as_string()
            server.sendmail(fromaddr, msg['To'], text)
            server.quit()


##### FUNCTION CALLS #####
connect_to_db(app)

send_recommendation_email()