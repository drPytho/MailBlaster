"""Mail Blaster."""
from email.message import EmailMessage
import configparser
import csv
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

    def load_receivers(self, columns, csv_file):
        """Polulate receivers with data."""
        with open(csv_file, 'r') as f:
            self.receivers = list(csv.DictReader(f, columns))

    def fmt(self, text, r):
        """Format the text with some information."""
        return text.format(**union_set(self.sender, r))

    def send(self, check_before_send=False, delay=0):
        """Send the emails."""
        # receivers := [{name, email}, ...]
        for r in self.receivers:
            msg = EmailMessage()
            msg['Subject'] = self.fmt(self.subject, r)
            msg['To'] = r['email']
            msg['From'] = self.sender['me_email']
            cont = self.fmt(self.content, r)
            msg.set_content(cont)
            mail_info = self.fmt('Sending mail to {name}, {email} from {me_email}', r)
            print(mail_info)
            if (check_before_send):
                print()
                print(cont)
                print()
                if (not ok('Looks good? ')):
                    continue

            self.smtp.send_message(msg)
            time.sleep(delay)

def union_set(a, b):
    t = {}
    for k in a: t[k] = a[k]
    for k in b: t[k] = b[k]
    return t

def ok(txt=""):
    """Print the text and ask if it's correct."""
    a = input(txt + ' [Y/n]: ')
    return a == "" or a == 'Y' or a == 'y'


def main():
    """Run the program."""
    conf = configparser.ConfigParser()
    conf.read('settings.ini')

    content = None
    with open(conf['mail']['template'], 'r') as f:
        content = f.read()

    me = {}
    for key in conf['me']:
        me['me_' + key] = conf['me'][key]

    print(me)
    print()
    print(content)

    if (not ok('Looks good?')):
        return

    mb = MailBlaster(me, conf['mail']['subject'], content)
    mb.auth(conf['server']['account'], conf['server']['password'])
    mb.load_receivers(conf['mail']['columns'].split(','),
                      conf['mail']['receivers'])
    mb.send()


if __name__ == '__main__':
    main()

