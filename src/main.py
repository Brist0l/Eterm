import argparse
import getpass
import hashlib
import json
import os
import readline
import smtplib
import socket
import subprocess
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import AutoCompleter
from colorama import Fore, init
import credsChecker


class EmailSender:
    def __init__(self):
        init(autoreset=True)
        self.parser = argparse.ArgumentParser(description="Send Emails through your terminal.",
                                              epilog="For more info check "
                                                     "my github page "
                                                     "https://github.com/"
                                                     "mrHola21/Eterm/")

        self.get_arguments()

        self.from_email = ""
        self.to_email = ""
        self.body_content_list = []
        self.body_content = ""
        self.files = []
        self.password = b""

        self.args = self.parser.parse_args() # For better extendibility in the future

        self.msg = MIMEMultipart()

        self.check_credentials()

    def get_arguments(self):
        self.parser.add_argument('from_', metavar="sender's email address", )
        self.parser.add_argument('--to', '-t', help="receiver's email address")
        self.parser.add_argument('--subject', '-s', action="store_true", help="Add Subject to your Email.")
        self.parser.add_argument('--body', '-b', action="store_true",
                                 help="Add the body to your Email")
        self.parser.add_argument('--file', '-f', type=str, nargs='+', help="Add Files to your emails , Enter the ")
        self.parser.add_argument('--list', '-l', action='store_true', help='Get the list of emails')

    def new_email(self):  # gets called if a new email is recognised
        password = bytes(
            getpass.getpass(
                f'This Is Your First Time Entering The Password For {Fore.BLUE}{self.args.from_} {Fore.RESET}:'),
            'utf8') # For keeping the passwd a secret 
        credsChecker.check(self.args.from_, password.decode('utf-8')) # External File Call
        hashed_pass = hashlib.sha512(password) # Hash the passwd for better security
        x = hashed_pass.hexdigest()
        json_format = {'gmail': self.args.from_,
                       'password': x} # Load it into a json format
        with open('pass.json', 'w+') as f:
            json.dump(json_format, f) # write json
        print(f"{Fore.CYAN}[+]Saved the Email and Password")
        print("Sending Email Now")
        self.check_credentials()

    def check_credentials(self):
        if os.stat('pass.json').st_size != 0:  # check if json file is empty 
            with open('pass.json', 'r') as password_file:  # password already there
                json_data = json.load(password_file)
                self.password = bytes(getpass.getpass(f'Enter Password for {Fore.BLUE} {self.args.from_}{Fore.RESET}:'),
                                      'utf-8')
                hashed = hashlib.sha512(self.password).hexdigest() # hash the current passwd to check with the passwd present in the json file
                if json_data['gmail'] == self.args.from_:  # checks if it is a new email or an old one
                    if str(json_data['password']) == str(hashed):  # check if its the right password
                        self.send_email_file()
                    else:
                        print(f'{Fore.RED}Wrong Password!{Fore.RESET}')
                        for i in range(1, 4):  # gives the user 3 tries to give the right password
                            self.password = bytes(
                                getpass.getpass(
                                    f'{Fore.RED}{i}{Fore.RESET} Wrong Password Enter Again for {Fore.BLUE}'
                                    f'{self.args.from_}{Fore.RESET}:'),
                                'utf8')
                            hashed = hashlib.sha512(self.password).hexdigest()
                            if json_data['password'] == str(hashed):  # if its right
                                self.send_email_file()
                            else:  # if its wrong it exits
                                pass
                        sys.exit(f'{Fore.RED}Wrong Password')
                else:
                    self.new_email()  # new email
        else:
            self.new_email() # File is empty . Creating a new email entry
                # This method leads to either `new_email()` or `send_email_file()` 
    def get_subject(self):
        try:
            subject_completer = AutoCompleter.MyCompleter(
                [greeting.strip() for greeting in open('Autocompletions/greeting.txt', 'r').readlines()])
            readline.set_completer(subject_completer.complete)
            readline.parse_and_bind('tab: complete')
            return input(f'{Fore.BLUE}Subject>{Fore.RESET}') if self.args.subject else None
        except KeyboardInterrupt:
            sys.exit('\n' + "Exiting ! Did Not Send The Email.")

    def get_body(self):
        if self.args.body:
            try:
                print(f'{Fore.LIGHTBLACK_EX}Hint:{Fore.RESET} Press {Fore.BLUE}Ctrl+C{Fore.RESET} to end the message!')
                while True:
                    line = input(f"{Fore.CYAN}Body>")
                    if line:
                        self.body_content_list.append(line)
                    else:
                        break
                    self.body_content = '\n'.join(self.body_content_list)
            except KeyboardInterrupt:
                print(f"\n\n{Fore.LIGHTGREEN_EX}Body done!\n\n")
                return self.body_content

    def get_recipients(self):
        self.from_email = self.args.from_
        self.to_email = self.args.to

    def send_email_file(self):
        self.get_recipients()
        self.msg['subject'] = self.get_subject()
        self.msg['from'] = self.from_email
        self.msg['to'] = self.to_email
        self.msg.attach(MIMEText(self.get_body() if self.args.body else "", 'plain')) # Empty Body if not specified
        if self.args.file:
            for file in self.args.file:
                with open(file, 'r') as f:
                    payload = MIMEBase('application', 'octet-stream')
                    payload.set_payload(f.read())
                    encoders.encode_base64(payload)
                    payload.add_header('Content-Disposition', 'attachment',
                                       filename=self.args.file[self.args.file.index(file)])
                    self.msg.attach(payload)
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as session:
                session.starttls()
                session.login(self.from_email, self.password.decode())
                msg = self.msg.as_string()
                session.sendmail(self.from_email, self.to_email, msg)
        except smtplib.SMTPAuthenticationError:
            sys.exit(
                "Allow less secure apps is in the OFF state by going to  "
                "https://myaccount.google.com/lesssecureapps . Turn it on and try again. "
                "make sure the Sender email & password are correct.")
        except socket.gaierror:
            sys.exit(f"{Fore.RED}Check your internet & firewall settings.")
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.GREEN} Email Send ")
        sys.exit(0)


if __name__ == '__main__':
    send = EmailSender()
