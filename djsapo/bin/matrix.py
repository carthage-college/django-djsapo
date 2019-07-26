# -*- coding: utf-8 -*-

import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djsapo.settings.shell')

import django
django.setup()

from django.conf import settings

from djsapo.core.models import Alert, GenericChoice, Member

import argparse
import logging

logger = logging.getLogger('djsapo')

'''
Shell script...
'''

# set up command-line options
desc = """
    Accepts as input an alert ID
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-a', '--aid',
    required=True,
    help="Alert ID",
    dest='aid'
)

def main():

    try:
        alert = Alert.objects.get(pk=aid)
    except Exception as e:
        print("alert does not exist")
        print("Exception: {}".format(str(e)))
        sys.exit(1)
    matrix = []
    team = [m.user for m in alert.team.all() if m.status]
    print("team = \n")
    print(team)
    print("\n")
    print("matrix = \n")
    for c in alert.category.all():
        #print(c.matrix.all())
        for m in c.matrix.all():
            if m.user not in matrix and m.user not in team:
                matrix.append(m.user)
    print(matrix)
    for user in matrix:
        print(user.groups.all())


######################
# shell command line
######################

if __name__ == '__main__':
    args = parser.parse_args()
    aid = args.aid

    sys.exit(main())
