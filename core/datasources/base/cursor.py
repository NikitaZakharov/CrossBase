class Cursor(object):

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, *args, **kwargs):
        return self._cursor.execute(*args, **kwargs)

    def fetchmany(self, *args, **kwargs):
        return self._cursor.fetchmany(*args, **kwargs)

    def fetchall(self, *args, **kwargs):
        return self._cursor.fetchall(*args, **kwargs)

    @property
    def description(self):
        return self._cursor.description

    @property
    def statusmessage(self):
        return self._cursor.statusmessage

    def close(self, *args, **kwargs):
        return self._cursor.close(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
