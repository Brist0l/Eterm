import sys
from smtplib import SMTP_SSL, SMTPAuthenticationError
from colorama import Fore


def check(email, password):
    with SMTP_SSL('smtp.gmail.com', 465) as session:
        try:
            session.login(email, password)
        except SMTPAuthenticationError:
            sys.exit(f'{Fore.RED}[-] Wrong credentials{Fore.RESET}')

