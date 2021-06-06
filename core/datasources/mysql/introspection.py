from core.datasources.base.introspection import Introspection as BaseIntrospection


class Introspection(BaseIntrospection):

    def get_tables(self, cursor):
        cursor.execute('SHOW TABLES')
        return [{'name': column[0], 'entity': 'table'} for column in sorted(cursor.fetchall())]

    def get_columns(self, cursor):
        columns = {}

        cursor.execute(
            """
            SELECT
                table_name,
                column_name,
                column_type,
                column_default,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
        """
        )

        for table, column, column_type, column_default, column_is_nullable in cursor.fetchall():
            columns.setdefault(table, []).append(
                {
                    'name': column,
                    'type': column_type,
                    'default': column_default,
                    'is_nullable': column_is_nullable == 'YES',
                    'entity': 'column',
                }
            )
        return columns

    def get_constraints(self, cursor):

        constraints = {}

        cursor.execute(
            """
            SELECT
                kc.table_name,
                kc.constraint_name,
                group_concat(kc.column_name),
                kc.referenced_table_name,
                kc.referenced_column_name,
                tc.constraint_type
            FROM information_schema.key_column_usage AS kc
            JOIN information_schema.table_constraints tc on tc.table_name = kc.table_name
            WHERE kc.table_schema = DATABASE()
            GROUP BY
                table_name, kc.constraint_name,
                kc.referenced_table_name, kc.referenced_column_name, tc.constraint_type;
        """
        )

        for table, constraint, columns, ref_table, ref_column, type_ in cursor.fetchall():
            constraints.setdefault(table, {}).setdefault(
                constraint,
                {
                    'columns': columns.split(','),
                    'is_primary_key': type_ == 'PRIMARY KEY',
                    'is_unique': type_ == 'UNIQUE',
                    'is_index': type_ == 'INDEX',
                    'is_check': False,
                    'foreign_key': (ref_table, ref_column) if ref_column else None,
                    'entity': type_.lower().replace(' ', '_'),
                },
            )

        cursor.execute(
            """
            SELECT
                table_name,
                index_name,
                group_concat(column_name),
                non_unique,
                index_type
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
            GROUP BY table_name, index_name, non_unique, index_type
        """
        )

        for table, index, columns, non_unique, type_ in cursor.fetchall():
            columns = columns.split(',')
            constraints.setdefault(table, {}).setdefault(
                index,
                {
                    'columns': columns,
                    'is_primary_key': False,
                    'is_unique': False,
                    'is_check': False,
                    'foreign_key': None,
                    'entity': 'index',
                },
            )
            constraints[table][index]['is_index'] = True
            constraints[table][index]['type'] = 'idx' if type_ == 'BTREE' else type_.lower()
            constraints[table][index]['columns'] = columns

        for table in constraints:
            constraints[table] = [{'name': k, **v} for k, v in constraints[table].items()]

        return constraints
