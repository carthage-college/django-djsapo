from django.core.cache import cache
from djimix.core.utils import get_connection


def get_peeps(who):
    key = 'provisioning_vw_{}_api'.format(who)
    peeps = cache.get(key)

    if peeps is None:

        if who == 'facstaff':
            where = 'faculty IS NOT NULL OR staff IS NOT NULL'
        elif who in ['faculty','staff','student']:
            where = '{} IS NOT NULL'.format(who)
        else:
            where = None

    if not peeps and where:
        sql = """
            SELECT
                lastname, firstname, username, id
            FROM
                provisioning_vw
            WHERE
                {}
            ORDER BY
                lastname, firstname
        """.format(where)

        connection = get_connection()
        cursor = connection.cursor()
        objects = cursor.execute(sql)

        if objects:
            peeps = []
            for obj in objects:
                row = {
                    'lastname': obj[0], 'firstname': obj[1],
                    'email': '{}@carthage.edu'.format(obj[2]),
                    'cid': obj[3]
                }
                peeps.append(row)
            cache.set(key, peeps, timeout=86400)

    return peeps
