import psycopg2

from core.datasources.base.connection import Connection as BaseConnection


__all__ = ['Connection', 'Error']


Error = psycopg2.Error


class Connection(BaseConnection):

    def __init__(self, *args, **kwargs):
        self._conn = psycopg2.connect(*args, **kwargs)

