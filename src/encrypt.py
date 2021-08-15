import hashlib
import sys

import main


def check():
    if open('pass.txt', 'r').read():  # password already there
        main.start()
    else:
        password = bytes(input('Enter Your Password:'), 'utf-8')
        with open('pass.txt', 'w+') as f:
            f.write(str(hashlib.sha512(password).digest()))


def get_pass():
    password = bytes(input("Enter Password:"), 'utf-8')
    hashed = hashlib.sha512(password).digest()
    real_pass = open('pass.txt', 'r').readline().strip()
    if str(hashed) == str(real_pass):
        print("nc")
    else:
        sys.exit("Wrong Password")


check()
