from core.datasources.base.introspection import Introspection as BaseIntrospection


class Introspection(BaseIntrospection):

    def get_tables(self, cursor):
        cursor.execute('SELECT table_name FROM user_tables ORDER BY table_name')
        return [{'name': table[0], 'entity': 'table'} for table in cursor.fetchall()]

    def get_columns(self, cursor):
        columns = {}
        cursor.execute(
            """
            SELECT
                table_name,
                column_name,
                data_type || '(' || data_length || ')',
                CASE WHEN nullable = 'Y' THEN 1 ELSE 0 END,
                data_default
            FROM user_tab_columns
        """
        )
        for table, column, type_, column_is_nullable, column_default in cursor.fetchall():
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
        constraints = {}
        # Loop over the constraints, getting PKs and uniques
        cursor.execute(
            """
            SELECT
                cons.table_name,
                cons.constraint_name,
                RTRIM(XMLAGG(XMLELEMENT(e, LOWER(cols.column_name), ',')
                ORDER BY cols.position).extract('//text()'), ','),
                CASE cons.constraint_type
                    WHEN 'P' THEN 1
                    ELSE 0
                END AS is_primary_key,
                1 AS is_unique
            FROM
                user_constraints cons
            LEFT OUTER JOIN
                user_cons_columns cols ON cons.constraint_name = cols.constraint_name
            WHERE
                cons.constraint_type = ANY('P', 'U')
            GROUP BY cons.table_name, cons.constraint_name, cons.constraint_type
        """
        )
        for table, constraint, columns, pk, unique in cursor.fetchall():
            constraints.setdefault(table, {}).setdefault(
                constraint,
                {
                    'columns': columns.split(','),
                    'is_primary_key': pk,
                    'is_unique': unique,
                    'foreign_key': None,
                    'is_index': unique,  # All uniques come with an index
                    'entity': 'primary_key' if pk else 'unique',
                },
            )
        # Foreign key constraints
        cursor.execute(
            """
            SELECT
                cons.table_name,
                cons.constraint_name,
                RTRIM(XMLAGG(XMLELEMENT(e, LOWER(cols.column_name), ',')
                ORDER BY cols.position).extract('//text()'), ','),
                LOWER(rcols.table_name),
                LOWER(rcols.column_name)
            FROM
                user_constraints cons
            INNER JOIN
                user_cons_columns rcols
            ON
                rcols.constraint_name = cons.r_constraint_name AND rcols.position = 1
            LEFT OUTER JOIN
                user_cons_columns cols ON cons.constraint_name = cols.constraint_name
            WHERE
                cons.constraint_type = 'R'
            GROUP BY cons.table_name, cons.constraint_name, rcols.table_name, rcols.column_name
        """
        )
        for table, constraint, columns, other_table, other_column in cursor.fetchall():
            constraints.setdefault(table, {})[constraint] = {
                'is_primary_key': False,
                'is_unique': False,
                'foreign_key': (other_table, other_column),
                'is_index': False,
                'columns': columns.split(','),
                'entity': 'foreign_key',
            }
        # Now get indexes
        cursor.execute(
            """
            SELECT
                cols.table_name,
                ind.index_name,
                LOWER(ind.index_type),
                RTRIM(XMLAGG(XMLELEMENT(e, LOWER(cols.column_name), ',')
                ORDER BY cols.column_position).extract('//text()'), ','),
                RTRIM(XMLAGG(XMLELEMENT(e, LOWER(cols.descend), ',')
                ORDER BY cols.column_position).extract('//text()'), ',')
            FROM
                user_ind_columns cols, user_indexes ind
            WHERE
                NOT EXISTS (
                    SELECT 1
                    FROM user_constraints cons
                    WHERE ind.index_name = cons.index_name
                ) AND cols.index_name = ind.index_name
            GROUP BY cols.table_name, ind.index_name, ind.index_type
        """
        )
        for table, constraint, type_, columns, orders in cursor.fetchall():
            constraints.setdefault(table, {})[constraint] = {
                'is_primary_key': False,
                'is_unique': False,
                'foreign_key': None,
                'is_index': True,
                'type': 'idx' if type_ == 'normal' else type_,
                'columns': columns.split(','),
                'orders': orders.split(','),
                'entity': 'index',
            }

        for table in constraints:
            constraints[table] = [{'name': k, **v} for k, v in constraints[table].items()]

        return constraints
