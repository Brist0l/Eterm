import argparse
import getpass
import hashlib
import json
import os
import readline
import smtplib
import socket
import sys
from email import encoders
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from colorama import Fore, init


class MyCompleter:

    def __init__(self, options):
        self.options = sorted(options)
        self.matches = None

    def complete(self, text, state):
        if state == 0:
            if text:
                self.matches = [s for s in self.options
                                if text in s]
            else:
                self.matches = self.options[:]

        try:
            return self.matches[state]
        except IndexError:
            return None


class Sender:
    def __init__(self):
        init(autoreset=True)
        self.parser = argparse.ArgumentParser(description="Send Emails through your terminal.")

        self.arguments()

        self.from_email = ""
        self.to_email = ""
        self.body_content = ""
        self.files = []
        self.password = b""

        self.fail = None
        self.success = None

        self.msg = EmailMessage()
        self.file_msg = MIMEMultipart()
        self.args = self.parser.parse_args()
        self.check()

    def arguments(self):
        self.parser.add_argument('frome', help="The Email from which you want to send the mail")
        self.parser.add_argument('to', help="The Email which you want to send the mail")
        self.parser.add_argument('--subject', '-s', action='store_true', help="Add Subject to your Email.")
        self.parser.add_argument('--body', '-b', type=int,
                                 help="Add the body to your Email , Enter the Number of lines.")
        self.parser.add_argument('--file', '-f', type=int, help="Add Files to your emails")

    def new_email(self):
        password = bytes(
            input(f'This Is Your First Time Entering The Password For {Fore.BLUE}{self.args.frome}{Fore.RESET}:'),
            'utf8')
        hashed_pass = hashlib.sha512(password)
        x = hashed_pass.hexdigest()
        json_format = {'gmail': self.args.frome,
                       'password': x}
        with open('pass.json', 'w+') as f:
            json.dump(json_format, f)

    def check(self):
        if os.stat('pass.json').st_size != 0:
            with open('pass.json', 'r') as password_file:  # password already there
                json_data = json.load(password_file)
                self.password = bytes(input(f'Enter Password for{Fore.BLUE} {self.args.frome}{Fore.RESET}:'), 'utf-8')
                hashed = hashlib.sha512(self.password).hexdigest()
                if json_data['gmail'] == self.args.frome:
                    if str(json_data['password']) == str(hashed):
                        self._decide()
                    else:
                        print('Wrong Password!')
                        for i in range(1, 4):
                            self.password = bytes(
                                input(
                                    f'{Fore.RED}{i}{Fore.RESET} Wrong Password Enter Again for{Fore.BLUE}{self.args.frome}{Fore.RESET}:'),
                                'utf8')
                            hashed = hashlib.sha512(self.password).hexdigest()
                            if json_data['password'] == str(hashed):
                                self._decide()
                            else:
                                pass
                        sys.exit(f'{Fore.RED}Wrong Pass This one')
                else:
                    self.new_email()  # new email
        else:
            self.new_email()

    def _decide(self):
        self.send_email_file() if self.args.file else self.send_email_no_file()

    def get_subject(self):
        try:
            subject_completer = MyCompleter(
                [greeting.strip() for greeting in open('Autocompletions/greeting.txt', 'r').readlines()])
            readline.set_completer(subject_completer.complete)
            readline.parse_and_bind('tab: complete')
            for kw in open('Autocompletions/greeting.txt', 'r').readlines():
                readline.add_history(kw)
            return input(f'{Fore.BLUE}Subject>{Fore.RESET}') if self.args.subject else None
        except KeyboardInterrupt:
            sys.exit('\n' + "Exiting ! Did Not Send The Email.")

    def get_body(self):
        try:
            MyCompleter([])
            for linenums in range(1, self.args.body + 1):
                self.body_content += input(f"Body {linenums}:") + "\n"
        except KeyboardInterrupt:
            sys.exit('\n' + self.fail.substitute(text="Exiting ! Did Not Send The Email."))

    def get_files(self):
        the_files = []
        # os.chdir(f'/home/{getpass.getuser()}')
        locations = [locations.strip() for locations in open('Autocompletions/files.txt', 'r').readlines()]
        for location in locations:
            [the_files.append(file) for file in os.listdir(location) if not file.startswith('.')]
        try:
            os_completions = MyCompleter(the_files)
            readline.set_completer(os_completions.complete)
            readline.parse_and_bind('tab: complete')
            for linenums in range(1, self.args.file + 1):
                self.files.append(input(f"File {linenums}:"))
        except KeyboardInterrupt:
            sys.exit('\n' + "Exiting ! Did Not Send The Email.")
        return self.files

    def get_reciptants(self):
        self.from_email = self.args.frome
        self.to_email = self.args.to

    def send_email_file(self):
        self.get_reciptants()
        self.file_msg['subject'] = self.get_subject()
        self.file_msg['from'] = self.from_email
        self.file_msg['to'] = self.to_email
        self.file_msg.attach(MIMEText(self.get_body() if self.args.body else "", 'plain'))
        self.get_files()
        for file in self.files:
            with open(file, 'r') as f:
                payload = MIMEBase('application', 'octate-stream')
                payload.set_payload(f.read())
                encoders.encode_base64(payload)
                payload.add_header('Content-Disposition', 'attachment', filename=self.files[self.files.index(file)])
                self.file_msg.attach(payload)
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as session:
                session.starttls()
                session.login(self.from_email, self.password.decode())
                msg = self.file_msg.as_string()
                session.sendmail(self.from_email, self.to_email, msg)
        except smtplib.SMTPAuthenticationError:
            sys.exit(
                "Allow less secure apps is in the OFF state by going to  "
                "https://myaccount.google.com/lesssecureapps . Turn it on and try again. "
                "make sure the Sender email & password are correct.")
        except socket.gaierror:
            sys.exit(f"{Fore.RED}Check your internet & firewall settings.")
        sys.exit(f"{Fore.GREEN}Done!")

    def send_email_no_file(self):
        self.get_reciptants()
        self.msg['subject'] = self.get_subject()
        self.msg['from'] = self.from_email
        self.msg['to'] = self.to_email
        self.msg.set_content(self.get_body() if self.args.body else "")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            try:
                smtp.login(self.from_email, self.password.decode())
                print('logged in')
                smtp.send_message(self.msg)
            except smtplib.SMTPAuthenticationError:
                sys.exit(
                    "Allow less secure apps is in the OFF state by going to  "
                    "https://myaccount.google.com/lesssecureapps . Turn it on and try again. "
                    "make sure the Sender email & password are correct.")
            except socket.gaierror:
                sys.exit(f"{Fore.RED}Check your internet & firewall settings.")
        print(f"{Fore.GREEN}Done!")


Sender()
