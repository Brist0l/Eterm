import argparse
import getpass
import hashlib
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
from string import Template
from colorama import Fore, init, Style


class MyCompleter:

    def __init__(self, options):
        self.options = sorted(options)
        self.matches = None

    def complete(self, text, state):
        if state == 0:
            if text:
                self.matches = [s for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]

        try:
            return self.matches[state]
        except IndexError:
            return None


class Sender:
    def __init__(self):
        # Initialising the modules
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

        self.templates()

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

    def templates(self):
        self.success = Template(f"{Style.BRIGHT}[{Fore.GREEN}{Fore.RESET}]{Style.RESET_ALL}$text")
        self.fail = Template(f"{Style.RESET_ALL}+{Style.BRIGHT}[{Fore.RED} - {Fore.RESET}] {Fore.RED}$text")

    def body(self):
        try:
            for linenums in range(1, self.args.body + 1):
                self.body_content += input(f"Body {linenums}:") + "\n"
        except KeyboardInterrupt:
            sys.exit('\n' + self.fail.substitute(text="Exiting ! Did Not Send The Email."))
        return self.body_content

    def get_files(self):
        the_files = []
        os.chdir(f'/home/{getpass.getuser()}')
        [the_files.append(file) for file in os.listdir() if not file.startswith('.')]
        try:
            os_completions = MyCompleter(the_files)
            readline.set_completer(os_completions.complete)
            readline.parse_and_bind('tab: complete')
            for linenums in range(1, self.args.file + 1):
                self.files.append(input(f"File {linenums}:"))
        except KeyboardInterrupt:
            sys.exit('\n' + self.fail.substitute(text="Exiting ! Did Not Send The Email."))
        return self.files

    def get_subject(self):
        try:
            subject_completer = MyCompleter(
                [greeting.strip() for greeting in open('Autocompletions/greeting.txt', 'r').readlines()])
            readline.set_completer(subject_completer.complete)
            readline.parse_and_bind('tab: complete')
            return input(f'{Fore.BLUE}Subject>{Fore.RESET}') if self.args.subject else None
        except KeyboardInterrupt:
            sys.exit('\n' + self.fail.substitute(text="Exiting ! Did Not Send The Email."))

    def get_pass(self):
        self.password = bytes(input("Enter Password:"), 'utf-8')
        hashed = hashlib.sha512(self.password).digest()
        real_pass = open('pass.txt', 'r').readline().strip()
        if str(hashed) == str(real_pass):
            self._decide()
        else:
            sys.exit("Wrong Password")

    def check(self):
        if open('pass.txt', 'r').read():  # password already there
            self.get_pass()
        else:
            password = bytes(input('Enter Your Password:'), 'utf-8')
            with open('pass.txt', 'w+') as f:
                f.write(str(hashlib.sha512(password).digest()))
            self.get_pass()

    def file(self):
        self.from_email = self.args.frome
        self.to_email = self.args.to
        self.file_msg['subject'] = self.get_subject()
        self.file_msg['from'] = self.from_email
        self.file_msg['to'] = self.to_email
        self.file_msg.attach(MIMEText(self.body() if self.args.body else "", 'plain'))
        self.get_files()
        for file in self.files:
            with open(file, 'r') as f:
                payload = MIMEBase('application', 'octate-stream')
                payload.set_payload(f.read())
                encoders.encode_base64(payload)
                payload.add_header('Content-Disposition', 'attachment', filename=self.files[self.files.index(file)])
                self.file_msg.attach(payload)
        try:
            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            print(self.password.decode())
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
        session.quit()
        print(self.success.substitute(text="Done!"))

    def send_email(self):
        self.from_email = self.args.frome
        self.to_email = self.args.to
        self.msg['subject'] = self.get_subject()
        self.msg['from'] = self.from_email
        self.msg['to'] = self.to_email
        self.msg.set_content(self.body() if self.args.body else "")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            try:
                smtp.login(self.from_email, str(self.password))
                smtp.send_message(self.msg)
            except smtplib.SMTPAuthenticationError:
                sys.exit(
                    "Allow less secure apps is in the OFF state by going to  "
                    "https://myaccount.google.com/lesssecureapps . Turn it on and try again. "
                    "make sure the Sender email & password are correct.")
            except socket.gaierror:
                sys.exit(f"{Fore.RED}Check your internet & firewall settings.")
        print(self.success.substitute(text="Done!"))

    def _decide(self):
        self.file() if self.args.file else self.send_email()


if __name__ == '__main__':
    Sender()
