# -*- coding: utf-8 -*-

import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djsapo.settings.shell')

import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import User, Group

import argparse
import logging

logger = logging.getLogger('djsapo')

'''
Obtain a list of users from a group
'''

# set up command-line options
desc = """
    Accepts as input a group name, which must be in quotes if the name
    contains spaces. e.g. "Hall Directors"
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-g', '--group',
    required=True,
    help="Group name",
    dest='group'
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

    # obtain all users who are a member of a particular group
    users = User.objects.filter(groups__name=group)
    for u in users:
        print(u)
    print('\n')
    # or obtain the users from reverse relationship and related name set
    g = Group.objects.get(name=group)
    users = g.user_set.all()
    for u in users:
        print(u)


######################
# shell command line
######################

if __name__ == '__main__':
    args = parser.parse_args()
    group = args.group
    test = args.test

    if test:
        print(args)

    sys.exit(main())

