import pymssql

from core.datasources.base.connection import Connection as BaseConnection


__all__ = ['Connection', 'Error']


Error = pymssql.Error


class Connection(BaseConnection):

    def __init__(self, *args, **kwargs):
        self._conn = pymssql.connect(*args, **kwargs)
