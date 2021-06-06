import clickhouse_driver

from core.datasources.base.connection import Connection as BaseConnection


__all__ = ['Connection', 'Error']


Error = clickhouse_driver.dbapi.Error


class Connection(BaseConnection):

    def __init__(self, *args, **kwargs):
        self._conn = clickhouse_driver.dbapi.connect(*args, **kwargs)
