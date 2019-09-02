# -*- coding: utf-8 -*-

import os, sys
# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djsapo.settings.shell')

# required if using django models
import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import Group, User
from djsapo.core.models import Alert

import argparse

'''
test djtools send_mail() function
'''

# set up command-line options
desc = """
Accepts as input an email address
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-e', '--email',
    required=True,
    help="email address of a user in the system",
    dest='email'
)
parser.add_argument(
    '-a', '--aid',
    required=True,
    help="ID of an Alert() object in the system",
    dest='aid'
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)

def main():
    '''
    main function
    '''

    from djtools.utils.mail import send_mail
    request = False
    alert = Alert.objects.get(pk=aid)
    user = User.objects.get(email=email)
    send_mail(
        request, [email,], "Assignment to Intervention Team",
        settings.CSS_FROM_EMAIL, 'alert/email_team_added.html',
        {'alert':alert,'user':user}, [settings.ADMINS[0][1],]
    )


######################
# shell command line
######################

if __name__ == '__main__':
    args = parser.parse_args()
    email = args.email
    aid = args.aid
    test = args.test

    if test:
        print(args)

    sys.exit(main())

