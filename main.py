import smtplib
import socket
import sys
from email.message import EmailMessage
import argparse
from colorama import Fore, init, Style
from string import Template


class Sender:
    def __init__(self):
        # Initialising the modules
        init(autoreset=True)
        self.parser = argparse.ArgumentParser(description="Send Emails through your terminal.")

        self.arguments()

        self.from_email = ""
        self.to_email = ""
        self.body_content = ""

        self.fail = None
        self.success = None

        self.templates()

        self.msg = EmailMessage()
        self.args = self.parser.parse_args()
        self.send_email()

    def arguments(self):
        self.parser.add_argument('frome', help="The Email from which you want to send the mail")
        self.parser.add_argument('to', help="The Email which you want to send the mail")
        self.parser.add_argument('--subject', '-s', action='store_true', help="Add Subject to your Email.")
        self.parser.add_argument('--body', '-b', type=int,
                                 help="Add the body to your Email , Enter the Number of lines.")

    def templates(self):
        # self.header = Template(
        #     f"\n{Style.BRIGHT}---------- [ {Fore.CYAN} $text {Fore.RESET} ] ----------\n")
        # self.prompt = Template(f"{Style.BRIGHT}[{Fore.BLUE}# {Fore.RESET}]{Style.RESET_ALL}$text : {Style.BRIGHT}")
        # self.code = Template(f"{Style.BRIGHT}{Fore.GREEN}$code")
        self.success = Template(f"{Style.BRIGHT}[{Fore.GREEN}{Fore.RESET}]{Style.RESET_ALL}$text")
        # self.info = Template(f"{Style.BRIGHT}[{Fore.YELLOW} ! {Fore.RESET}] {Style.RESET_ALL}$text")
        self.fail = Template(f"{Style.RESET_ALL} {Style.BRIGHT}[{Fore.RED} - {Fore.RESET}] {Fore.RED}$text")

    def body(self):
        try:
            for linenums in range(1, self.args.body + 1):
                self.body_content += input(f"Subject{linenums}:") + "\n"
        except KeyboardInterrupt:
            sys.exit('\n' + self.fail.substitute(text="Exiting ! Did Not Send The Email."))
        return self.body_content

    def send_email(self):
        self.from_email = self.args.frome
        self.to_email = self.args.to
        try:
            self.msg['subject'] = input(f'{Fore.BLUE}Subject>') if self.args.subject else None
        except KeyboardInterrupt:
            sys.exit('\n' + self.fail.substitute(text="Exiting ! Did Not Send The Email."))

        self.msg['from'] = self.from_email
        self.msg['to'] = self.to_email
        self.msg.set_content(self.body() if self.args.body else None)

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
                sys.exit(f"{Fore.RED}Check your internet & firewall settings.")


Sender()
