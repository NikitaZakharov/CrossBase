import mysql.connector

from core.datasources.base.connection import Connection as BaseConnection


__all__ = ['Connection', 'Error']


Error = mysql.connector.Error


class Connection(BaseConnection):

    def __init__(self, *args, **kwargs):
        self._conn = mysql.connector.connect(*args, **kwargs)
