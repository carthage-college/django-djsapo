# -*- coding: utf-8 -*-

import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djsapo.settings.shell')

import django
django.setup()

from django.conf import settings
from django.urls import reverse
from django.core.cache import cache

from djsapo.core.utils import get_peeps

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
        peeps = get_peeps(key)

if __name__ == '__main__':
    sys.exit(main())

