from core.datasources.base.introspection import Introspection as BaseIntrospection


class Introspection(BaseIntrospection):

    def get_tables(self, cursor):
        cursor.execute(
            """
            SELECT
                tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """
        )
        return [{'name': table[0], 'entity': 'table'} for table in cursor.fetchall()]

    def get_columns(self, cursor):
        columns = {}
        cursor.execute(
            """
            SELECT
                columns.table_name AS table_name,
                columns.column_name AS column_name,
                CASE
                    WHEN columns.data_type = 'character varying' THEN
                        'varchar(' || character_maximum_length || ')'
                    ELSE columns.data_type
                END AS column_type,
                columns.column_default AS column_default,
                CASE
                    WHEN columns.is_nullable = 'NO' THEN
                        FALSE
                    ELSE
                        TRUE
                END AS column_is_nullable
            FROM pg_catalog.pg_tables tables
            JOIN information_schema.columns columns
                ON tables.tablename = columns.table_name AND tables.schemaname = 'public'
        """
        )
        for table, column, column_type, column_default, column_is_nullable in cursor.fetchall():
            columns.setdefault(table, []).append(
                {
                    'name': column,
                    'type': column_type,
                    'default': column_default,
                    'is_nullable': column_is_nullable,
                    'entity': 'column',
                }
            )
        return columns

    def get_constraints(self, cursor):
        constraints = {}

        cursor.execute(
            """
            SELECT
                cl.relname,
                c.conname,
                array(
                    SELECT attname
                    FROM (
                        SELECT unnest(c.conkey) AS colid,
                               generate_series(1, array_length(c.conkey, 1)) AS arridx
                    ) AS cols
                    JOIN pg_attribute AS ca ON cols.colid = ca.attnum
                    WHERE ca.attrelid = c.conrelid
                    ORDER BY cols.arridx
                ),
                c.contype,
                (SELECT fkc.relname || '.' || fka.attname
                FROM pg_attribute AS fka
                JOIN pg_class AS fkc ON fka.attrelid = fkc.oid
                WHERE fka.attrelid = c.confrelid AND fka.attnum = c.confkey[1])
            FROM pg_constraint AS c
            JOIN pg_class AS cl ON c.conrelid = cl.oid
            JOIN pg_namespace AS ns ON cl.relnamespace = ns.oid AND ns.nspname = 'public'
        """
        )

        for table, constraint, columns, kind, foreign_key in cursor.fetchall():
            constraints.setdefault(table, {}).setdefault(
                constraint,
                {
                    'columns': columns,
                    'is_primary_key': kind == 'p',
                    'is_unique': kind in ['p', 'u'],
                    'foreign_key': tuple(foreign_key.split('.', 1)) if kind == 'f' else None,
                    'is_check': kind == 'c',
                    'is_index': kind == 'u',
                    'entity': {'p': 'primary_key', 'f': 'foreign_key', 'c': 'check', 'u': 'unique'}.get(kind, 'index'),
                },
            )
        # Now get indexes
        # The row_number() function for ordering the index fields can be
        # replaced by WITH ORDINALITY in the unnest() functions when support
        # for PostgreSQL 9.3 is dropped.
        cursor.execute(
            """
            SELECT
                tablename, indexname, array_agg(attname ORDER BY rnum), indisunique, indisprimary,
                array_agg(ordering ORDER BY rnum), amname
            FROM (
                SELECT
                    row_number() OVER () as rnum, c.relname AS tablename, c2.relname as indexname,
                    idx.*, attr.attname, am.amname, c.relnamespace,
                    CASE
                        WHEN idx.indexprs IS NOT NULL THEN
                            pg_get_indexdef(idx.indexrelid)
                    END AS exprdef,
                    CASE am.amname
                        WHEN 'btree' THEN
                            CASE (option & 1)
                                WHEN 1 THEN 'DESC' ELSE 'ASC'
                            END
                    END as ordering,
                    c2.reloptions as attoptions
                FROM (
                    SELECT
                        *, unnest(i.indkey) as key, unnest(i.indoption) as option
                    FROM pg_index i
                ) idx
                LEFT JOIN pg_class c ON idx.indrelid = c.oid
                LEFT JOIN pg_class c2 ON idx.indexrelid = c2.oid
                LEFT JOIN pg_am am ON c2.relam = am.oid
                LEFT JOIN pg_attribute attr ON attr.attrelid = c.oid AND attr.attnum = idx.key
            ) s2
            JOIN pg_namespace AS ns ON s2.relnamespace = ns.oid AND ns.nspname = 'public'
            GROUP BY tablename, indexname, indisunique, indisprimary, amname, exprdef, attoptions;
        """
        )
        for table, index, columns, unique, primary, orders, type_ in cursor.fetchall():
            constraints.setdefault(table, {}).setdefault(
                index,
                {
                    'columns': columns if columns != [None] else [],
                    'orders': orders if orders != [None] else [],
                    'is_primary_key': primary,
                    'is_unique': unique,
                    'foreign_key': None,
                    'is_check': False,
                    'is_index': True,
                    'entity': 'index',
                },
            )

        for table in constraints:
            constraints[table] = [{'name': k, **v} for k, v in constraints[table].items()]

        return constraints
