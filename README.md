# django-djsapo
Early Alert application for community members to voice their concern about
another member of the community.

# cron
00 02 * * * (cd /data2/python_venv/3.6/djsapo/ && . bin/activate && bin/python djsapo/bin/clear_cache.py) >> /dev/null 2>&1
