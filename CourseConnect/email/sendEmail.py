import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd
import os


class CourseConnect:

    def __init__(self):
        self.senders_email = 'courseconnect.scu@gmail.com'
        self.senders_pwd = 'app_password' # app password

    def jsonToXlsx(self, data):
        # Convert json to dataframe
        df = pd.json_normalize(data)

        # Write dataframe to excel file
        xls_file = os.path.join(os.getcwd(), 'CourseConnect.xlsx')
        df.to_excel(xls_file, index=False)

        # Return course and xls file path
        return xls_file

    def send_email(self,receiver_email, course, xls_file):
        # create the email message
        msg = MIMEMultipart()
        msg['From'] = self.senders_email
        msg['To'] = receiver_email
        msg['Subject'] = f'CourseConnect {course} Subscription'

        # create the email body
        body = f"Dear Bronco,\n\nThank you for subscribing to CourseConnect. "
        body += f"We have attached the list of users for {course} in the upcoming quarter\n\n"

        # Read data from the Excel file and format it as a table
        df = pd.read_excel(xls_file)
        table = df.to_html(index=False)

        body += f"\n\nBest regards,\nTeam CourseConnect"
        msg.attach(MIMEText(body, 'plain'))

        # create the attachment (the Excel file)
        with open(xls_file, 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='xlsx')
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(xls_file))
            msg.attach(attachment)

        # send the email
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = self.senders_email
        smtp_password = self.senders_pwd

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, msg['To'], msg.as_string())
        print(f"Email sent successfully to {receiver_email}")


if __name__ == '__main__':
    #declarimg the variables which CE will parse
    receivers = ['dmahajan2@scu.edu', 'myerolkar@scu.edu','rbshah@scu.edu','rlagare@scu.edu']
    course = 'testCOEN247'

    #fetching json file for testing purpose
    folder1 = 'CourseConnect'
    path = os.getcwd()
    json_filepath = os.path.join(path, folder1, "subscribed.json")
    # load the JSON file into a variable
    with open(json_filepath) as json_file:
        data = (json.load(json_file))

    for receiver_email in receivers:
        #testing with test data created above
        cc = CourseConnect()
        xls_file = cc.jsonToXlsx(data)
        cc.send_email(receiver_email, course, xls_file)
