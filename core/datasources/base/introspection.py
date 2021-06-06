import abc

from core.datasources.base.connection import Connection
from core.datasources.base.cursor import Cursor


class Introspection(abc.ABC):

    def __init__(self, connection: Connection):
        self.connection = connection

    @abc.abstractmethod
    def get_tables(self, cursor: Cursor):
        pass

    @abc.abstractmethod
    def get_columns(self, cursor: Cursor):
        pass

    @abc.abstractmethod
    def get_constraints(self, cursor: Cursor):
        pass

    def get_structure(self):
        with self.connection.cursor() as cursor:
            tables = self.get_tables(cursor)
            columns = self.get_columns(cursor)
            constraints = self.get_constraints(cursor)
            return [
                {**table, 'children': columns.get(table['name'], []) + constraints.get(table['name'], [])}
                for table in tables
            ]
