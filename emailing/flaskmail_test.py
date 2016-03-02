from flask import Flask
from flask_mail import Mail, Message
import os

app=Flask(__name__)
# mail=Mail(app)

app.secret_key="ABCD"

app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_SSL=False,
    MAIL_USE_TLS=True,
    MAIL_USERNAME = os.environ.get('NEXTBOOK_GMAIL'),
    MAIL_PASSWORD = os.environ.get('NEXTBOOK_GMAIL_PW'),
    MAIL_DEFAULT_SENDER = os.environ.get('NEXTBOOK_GMAIL')
    ))

mail=Mail(app)

@app.route("/")
def mailer():
    msg = Message(
              subject='Hello',
           recipients=['emmamferguson@gmail.com'],
           body="This is the email body.")
           # sender=os.environ.get('NEXTBOOK_GMAIL'))
    # print msg.sender
    with app.app_context():
        mail.send(msg)    
    return "Sent"

if __name__ == "__main__":
    app.run()