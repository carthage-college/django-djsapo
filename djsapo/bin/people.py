# -*- coding: utf-8 -*-

import os, sys
# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djsapo.settings')

# required if using django models
import django
django.setup()

from django.conf import settings

import pyodbc
import argparse
import logging

logger = logging.getLogger('djsapo')

# set up command-line options
desc = """
Accepts as input a group type: student, faculty, or staff
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-w', '--who',
    required=True,
    help="student, faculty, staff",
    dest='who'
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

    sql = """
        SELECT
            *
        FROM
            provisioning_vw
        WHERE
            {} is not null
        ORDER BY
            lastname, firstname
        LIMIT 10
    """.format(who)

    if test:
        print("sql = {}".format(sql))
        logger.debug("sql = {}".format(sql))
    else:
        connection = get_connection()
        #connection.setencoding(encoding='cp1252', ctype=pyodbc.SQL_CHAR)
        #connection.setencoding(encoding='latin1', ctype=pyodbc.SQL_CHAR)
        connection.setencoding(encoding='utf-8', ctype=pyodbc.SQL_CHAR)
        cursor = connection.cursor()
        objects = cursor.execute(sql)
        for o in objects:
            print(o[2],o[1])


######################
# shell command line
######################

if __name__ == '__main__':
    args = parser.parse_args()
    equis = args.equis
    test = args.test

    if test:
        print(args)

    sys.exit(main())

