import smtplib
import os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Message info
fromaddr = os.environ.get("NEXTBOOK_GMAIL")
toaddr  = "user@email.com"

msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "This is a subject test"

body = "the medium is the message."
msg.attach(MIMEText(body, 'plain'))

# Credentials
username = fromaddr
password = os.environ.get("NEXTBOOK_GMAIL_PW")

# The actual mail send
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username,password)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()