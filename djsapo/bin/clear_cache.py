# -*- coding: utf-8 -*-

import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djsapo.settings.shell')

import django
django.setup()

from django.conf import settings
from django.urls import reverse
from django.core.cache import cache

from djimix.people.utils import get_peeps

# informix environment
os.environ['INFORMIXSERVER'] = settings.INFORMIXSERVER
os.environ['DBSERVERNAME'] = settings.DBSERVERNAME
os.environ['INFORMIXDIR'] = settings.INFORMIXDIR
os.environ['ODBCINI'] = settings.ODBCINI
os.environ['ONCONFIG'] = settings.ONCONFIG
os.environ['INFORMIXSQLHOSTS'] = settings.INFORMIXSQLHOSTS
os.environ['LD_LIBRARY_PATH'] = settings.LD_LIBRARY_PATH
os.environ['LD_RUN_PATH'] = settings.LD_RUN_PATH

# set up command-line options
desc = """
    clear the cache and repopulate it for API data
"""


def main():
    '''
    main function
    '''

    headers = {'Cache-Control': 'no-cache'}
    for key in ['student','facstaff']:
        cache.delete('provisioning_vw_{}_api'.format(key))
        try:
            peeps = get_peeps(key)
        except Exception as error:
            print(error)


if __name__ == '__main__':
    sys.exit(main())

