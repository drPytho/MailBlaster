"""Mail Blaster."""
from email.message import EmailMessage
import argparse
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

    def set_recivers(self, recivers):
        """Set reciver data."""
        self.recivers = recivers

    def load_recivers(self, csv_file):
        """Polulate recivers with data."""
        with open(csv_file, 'r') as f:
            self.recivers = list(csv.DictReader(f, ['name', 'email']))

    def fmt(self, text, r):
        """Format the text with some information."""
        return text.format(
            name=r.get('name'),
            email=r.get('email'),
            my_name=self.sender.get('name'),
            my_email=self.sender.get('email'),
            my_phone=self.sender.get('phone'))

    def send(self, delay=0):
        """Send the emails."""
        # recivers := [{name, email}, ...]
        for r in self.recivers:
            msg = EmailMessage()
            msg['Subject'] = self.fmt(self.subject, r)
            msg['To'] = r['email']
            msg['From'] = self.sender['email']
            msg.set_content(self.fmt(self.content, r))
            ok(self.fmt('Sending mail to {name}:{email} from {my_email}', r))
            self.smtp.send_message(msg)
            time.sleep(delay)


def ok(txt):
    """Print the text and ask if it's correct."""
    print(txt)
    a = input('Looks good? [Y/n]: ')
    return a == "" or a == 'Y' or a == 'y'


def main():
    """Run the program."""

    parser = argparse.ArgumentParser(description='Do a MailBlast!')
    parser.add_argument('-s', '--subject', help='Subject of email (can be foramted).')
    parser.add_argument('-t', '--template',  help='Select template for mail.')
    parser.add_argument('-r', '--recivers', help='A csv file with "name,email"')

    args = parser.parse_args()
    print(args.subject)
    
    content = ""
    with open(args.template, 'r') as f:
        content = f.read()

    if (not ok(content)):
        return

    me = {
        'name': 'Filip Lindvall',
        'email': 'sales@d.kth.se',
        'phone': '0733211420'
    }

    mb = MailBlaster(me, args.subject, content)
    mb.auth('flindv', os.environ['mailpasswd'])
    mb.load_recivers(args.recivers)
    mb.send()


if __name__ == '__main__':
    main()

