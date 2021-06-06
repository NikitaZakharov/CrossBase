from core.datasources.base.introspection import Introspection as BaseIntrospection


class Introspection(BaseIntrospection):

    def get_tables(self, cursor):
        cursor.execute('SELECT name FROM system.tables WHERE database = currentDatabase() ORDER BY name')
        return [{'name': table[0], 'entity': 'table'} for table in cursor.fetchall()]

    def get_columns(self, cursor):
        columns = {}
        cursor.execute(
            """
            SELECT
                table,
                name,
                type,
                CASE
                    WHEN default_kind = '' THEN
                        NULL
                    ELSE
                        default_expression
                END AS column_default,
                type LIKE 'Nullable(%%)' AS is_nullable
            FROM system.columns
            WHERE database = currentDatabase()
            FORMAT JSON
        """
        )
        for table, column, type_, column_default, column_is_nullable in cursor.fetchall():
            columns.setdefault(table, []).append(
                {
                    'name': column,
                    'type': type_,
                    'default': column_default,
                    'is_nullable': column_is_nullable,
                    'entity': 'column',
                }
            )
        return columns

    def get_constraints(self, cursor):
        return {}
