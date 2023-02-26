import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd
import os
  
folder1 = 'CourseConnect'
folder2 = 'courses'
senders_email = 'sender_email@scu.edu'
receiver_email = 'receiver_email@scu.edu'
course = 'testCourseNo'
path = os.getcwd()
json_filepath = os.path.join(path, "CourseConnect", "userInput.json")
# load the JSON file into a variable
with open(json_filepath) as json_file:
    data = (json.load(json_file))
# data = json.dumps(data)

# create the email message
msg = MIMEMultipart()
msg['From'] = senders_email
msg['To'] = receiver_email
msg['Subject'] = f'CourseConnect {course} subscription'

# create the email body
body = f"Dear Bronco,\n\nThank You for subscribing to CourseConnect"
body += f"Below is the list of users for {course} in upcoming quarter:"
body += f"\n\n{data}\n\nBest regards,\nTeam CourseConnect"
msg.attach(MIMEText(body, 'plain'))

# create the attachment (the JSON file)
attachment = MIMEApplication(json.dumps(data), _subtype='json')
attachment.add_header('Content-Disposition', 'attachment', filename='data.json')
msg.attach(attachment)

# send the email
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'sender_email@example.com'
smtp_password = 'your_password'

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(smtp_username, msg['To'], msg.as_string())
