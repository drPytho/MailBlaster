"""Mail Blaster."""
from email.message import EmailMessage
import argparse
import configparser
import csv
import os
import smtplib
import sys
import time


class MailBlaster:
    def __init__(self, sender, subject, content):
        """Create the MailBlaster."""
        self.sender = sender
        self.content = content
        self.subject = subject

        try:
            self.smtp = smtplib.SMTP_SSL('smtp.kth.se')
        except Exception as e:
            print('Could not connect to mail server')
            print(e)
            sys.exit(1)

    def auth(self, user, password):
        """Authenticate to the mail server."""
        try:
            self.smtp.login(user, password)
        except Exception as e:
            print('Login Failed')
            print(e)
            sys.exit(1)

    def load_receivers(self, csv_file):
        """Polulate receivers with data."""
        with open(csv_file, 'r') as f:
            self.receivers = list(csv.DictReader(f, ['name', 'email']))

    def fmt(self, text, r):
        """Format the text with some information."""
        return text.format(
            name=r.get('name'),
            email=r.get('email'),
            my_name=self.sender.get('name'),
            my_email=self.sender.get('email'),
            my_phone=self.sender.get('phone'))

    def send(self, check_before_send=False, delay=0):
        """Send the emails."""
        # receivers := [{name, email}, ...]
        for r in self.receivers:
            msg = EmailMessage()
            msg['Subject'] = self.fmt(self.subject, r)
            msg['To'] = r['email']
            msg['From'] = self.sender['email']
            cont = self.fmt(self.content, r)
            msg.set_content(cont)
            mail_info = self.fmt('Sending mail to {name}, {email} from {my_email}', r)
            print(mail_info)
            if (check_before_send):
                print()
                print(cont)
                print()
                if (not ok('Looks good? ')):
                    continue

            self.smtp.send_message(msg)
            time.sleep(delay)


def ok(txt=""):
    """Print the text and ask if it's correct."""
    a = input(txt + ' [Y/n]: ')
    return a == "" or a == 'Y' or a == 'y'


def main():
    """Run the program."""
    conf = configparser.ConfigParser()
    conf.read('settings.ini')
    
    content = None
    with open(conf['info']['template'], 'r') as f:
        content = f.read()

    me = {
        'name': conf['me']['name'],
        'email': conf['me']['email'],
        'phone': conf['me'].get('phone', '')
    }

    print(me)
    print()
    print(content)

    if (not ok('Looks good?')):
        return

    mb = MailBlaster(me, conf['info']['subject'], content)
    mb.auth(conf['secret']['account'], conf['secret']['password'])
    mb.load_receivers(conf['info']['receivers'])
    mb.send()


if __name__ == '__main__':
    main()

