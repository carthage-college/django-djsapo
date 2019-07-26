# -*- coding: utf-8 -*-

import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djsapo.settings.shell')

import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from djsapo.core.models import Alert, Member

import argparse

# set up command-line options
desc = """
    dashboard listing maquette for permissions
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-u', '--username',
    required=True,
    help="LDAP username",
    dest='username'
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

    from operator import attrgetter
    from itertools import chain

    team_alerts=[]
    user = User.objects.get(username=username)
    alerts = Alert.objects.filter(created_by=user)
    teams = Member.objects.filter(user__username="akrusza")
    team_alerts = [member.alert for member in teams]
    result_list = sorted(
        chain(alerts, team_alerts), key=attrgetter('created_at')
    )
    print(result_list)

if __name__ == '__main__':
    args = parser.parse_args()
    username = args.username
    test = args.test

    if test:
        print(args)

    sys.exit(main())

