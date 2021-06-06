import cx_Oracle

from core.datasources.base.connection import Connection as BaseConnection


__all__ = ['Connection', 'Error']


Error = cx_Oracle.Error


class Connection(BaseConnection):

    def __init__(self, *args, **kwargs):
        dsn = cx_Oracle.makedsn(kwargs.pop('host'), int(kwargs.pop('port')), kwargs.pop('database'))
        self._conn = cx_Oracle.connect(*args, **kwargs, dsn=dsn)
