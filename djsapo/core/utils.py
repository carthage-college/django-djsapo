from django.conf import settings

import pyodbc


def get_connection(earl=None):
    """
    establish an ODBC connection to a database
    """
    if not earl:
        earl = settings.INFORMIX_ODBC

    cnxn = pyodbc.connect(earl)
    #cnxn.setencoding(encoding='utf-8', ctype=pyodbc.SQL_CHAR)
    #cnxn.setencoding(encoding='utf8', ctype=pyodbc.SQL_CHAR)
    #cnxn.setencoding(encoding='latin1', ctype=pyodbc.SQL_CHAR)
    #cnxn.setencoding(encoding='cp1252', ctype=pyodbc.SQL_CHAR)

    cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='UTF-8')
    cnxn.setdecoding(pyodbc.SQL_CHAR, encoding='UTF-8')
    cnxn.setencoding(encoding='UTF-8')

    return cnxn
