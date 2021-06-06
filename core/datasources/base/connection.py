from core.datasources.base.cursor import Cursor as BaseCursor


__all__ = ['Connection', 'Error']


class Error(Exception):
    pass


class Connection(object):

    _conn = None

    def close(self, *args, **kwargs):
        return self._conn.close(*args, **kwargs)

    def commit(self, *args, **kwargs):
        return self._conn.commit(*args, **kwargs)

    def rollback(self, *args, **kwargs):
        return self._conn.rollback(*args, **kwargs)

    def cursor(self, *args, **kwargs):
        return BaseCursor(self._conn.cursor(*args, **kwargs))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
