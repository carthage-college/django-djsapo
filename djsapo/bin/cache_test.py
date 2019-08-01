# -*- coding: utf-8 -*-

import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djsapo.settings.shell')

import django
django.setup()

from django.conf import settings
from django.utils.safestring import mark_safe

import requests
import datetime
import argparse
import logging
import json

logger = logging.getLogger('djsapo')

# set up command-line options
desc = """
    test clearing the  cache
"""

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter
)

def main():
    '''
    main function
    '''
    ctype='blurbs'
    cid=2810
    timestamp = timestamp = datetime.datetime.timestamp(datetime.datetime.now())
    key = 'livewhale_{}_{}'.format(ctype,cid)
    earl = '{}/live/{}/{}@JSON?cache={}'.format(settings.LIVEWHALE_API_URL,ctype,cid,timestamp)
    print(earl)
    try:
        #headers = {'Cache-Control': 'public, max-age=0'}
        headers = {'Cache-Control': 'no-cache'}
        response = requests.get(earl, headers=headers)
        print(response.headers)
        content = json.loads(response.text)
        content = mark_safe(content['body'])
        print("content = {}".format(content))
    except:
        content = ''


if __name__ == '__main__':
    sys.exit(main())

