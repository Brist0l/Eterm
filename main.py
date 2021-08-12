import smtplib
import socket
import sys
from email.message import EmailMessage
import argparse


class Sender:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Send EMails through your terminal.")

        self.arguments()

        self.from_email = ""
        self.to_email = ""

        self.msg = EmailMessage()
        self.args = self.parser.parse_args()
        self.send_email()

    def arguments(self):
        self.parser.add_argument('frome', help="The Email from which you want to send the mail")
        self.parser.add_argument('to', help="The Email which you want to send the mail")
        self.parser.add_argument('--subject', '-s', type=str, help="Add Subject to your Email.")

    def send_email(self):
        self.from_email = self.args.frome
        self.to_email = self.args.to
        self.msg['subject'] = self.args.subject
        self.msg['from'] = self.from_email
        self.msg['to'] = self.to_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            try:
                smtp.login(self.from_email, password="")
                smtp.send_message(self.msg)
            except smtplib.SMTPAuthenticationError:
                sys.exit(
                    "Allow less secure apps is in the OFF state by going to  "
                    "https://myaccount.google.com/lesssecureapps . Turn it on and try again. "
                    "make sure the Sender email & password are correct.")
            except socket.gaierror:
                sys.exit("Check with your internet & firewall settings.")


Sender()
