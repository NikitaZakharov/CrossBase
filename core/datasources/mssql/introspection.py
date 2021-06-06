from core.datasources.base.introspection import Introspection as BaseIntrospection


class Introspection(BaseIntrospection):

    def get_tables(self, cursor):
        cursor.execute(
            """
            SELECT
                TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = SCHEMA_NAME()
            ORDER BY TABLE_NAME
        """
        )
        return [{'name': table[0], 'entity': 'table'} for table in cursor.fetchall()]

    def get_columns(self, cursor):
        columns = {}
        cursor.execute(
            """
            SELECT
                table_name,
                column_name,
                IIF(
                    character_maximum_length IS NOT NULL,
                    CONCAT(data_type, '(', character_maximum_length, ')'),
                    data_type
                ),
                column_default,
                IIF(is_nullable = 'NO', 0, 1)
            FROM information_schema.columns
            WHERE table_schema = schema_name();
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
        constraints = {}
        # get PKs, FKs, and uniques, but not CHECK
        cursor.execute(
            """
            SELECT
                kc.table_name,
                kc.constraint_name,
                kc.column_name,
                tc.constraint_type,
                fk.referenced_table_name,
                fk.referenced_column_name
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kc
            INNER JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
            ON
                kc.table_schema = tc.table_schema AND
                kc.table_name = tc.table_name AND
                kc.constraint_name = tc.constraint_name
            LEFT OUTER JOIN (
                SELECT
                    ps.name AS table_schema,
                    pt.name AS table_name,
                    pc.name AS column_name,
                    rt.name AS referenced_table_name,
                    rc.name AS referenced_column_name
                FROM sys.foreign_key_columns fkc
                INNER JOIN sys.tables pt
                ON
                    fkc.parent_object_id = pt.object_id
                INNER JOIN sys.schemas ps
                ON
                    pt.schema_id = ps.schema_id
                INNER JOIN sys.columns pc
                ON
                    fkc.parent_object_id = pc.object_id AND
                    fkc.parent_column_id = pc.column_id
                INNER JOIN sys.tables rt
                ON
                    fkc.referenced_object_id = rt.object_id
                INNER JOIN sys.schemas rs
                ON
                    rt.schema_id = rs.schema_id
                INNER JOIN sys.columns rc
                ON
                    fkc.referenced_object_id = rc.object_id AND
                    fkc.referenced_column_id = rc.column_id
            ) fk
            ON
                kc.table_schema = fk.table_schema AND
                kc.table_name = fk.table_name AND
                kc.column_name = fk.column_name
            WHERE
                kc.table_schema = SCHEMA_NAME()
            ORDER BY
                kc.constraint_name,
                kc.ordinal_position
        """
        )
        for table, constraint, column, kind, ref_table, ref_column in cursor.fetchall():
            # If we're the first column, make the record
            constraints.setdefault(table, {}).setdefault(
                constraint,
                {
                    'columns': [],
                    'is_primary_key': kind.lower() == 'primary key',
                    'is_unique': kind.lower() in ('primary key', 'unique'),
                    'foreign_key': (ref_table, ref_column) if kind.lower() == 'foreign key' else None,
                    'is_check': False,
                    'is_index': False,
                    'orders': [],
                    'entity': kind.lower().replace(' ', '_'),
                },
            )
            # Record the details
            constraints[table][constraint]['columns'].append(column)
        # get CHECK constraint columns
        cursor.execute(
            """
            SELECT
                kc.table_name,
                kc.constraint_name,
                kc.column_name
            FROM INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE AS kc
            JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS c
            ON
                kc.table_schema = c.table_schema AND
                kc.table_name = c.table_name AND
                kc.constraint_name = c.constraint_name
            WHERE
                c.constraint_type = 'CHECK' AND
                kc.table_schema = SCHEMA_NAME()
        """
        )
        for table, constraint, column in cursor.fetchall():
            # If we're the first column, make the record
            constraints.setdefault(table, {}).setdefault(
                constraint,
                {
                    'columns': [],
                    'is_primary_key': False,
                    'is_unique': False,
                    'foreign_key': None,
                    'is_check': True,
                    'is_index': False,
                    'orders': [],
                    'entity': 'check',
                },
            )
            # record the details
            constraints[table][constraint]['columns'].append(column)
        # get indexes
        cursor.execute(
            """
            SELECT
                t.name,
                i.name,
                i.is_unique,
                i.is_primary_key,
                i.type,
                i.type_desc,
                ic.is_descending_key,
                c.name AS column_name
            FROM sys.tables AS t
            INNER JOIN sys.schemas AS s
            ON
                t.schema_id = s.schema_id
            INNER JOIN sys.indexes AS i
            ON
                t.object_id = i.object_id
            INNER JOIN sys.index_columns AS ic
            ON
                i.object_id = ic.object_id AND
                i.index_id = ic.index_id
            INNER JOIN sys.columns AS c
            ON
                ic.object_id = c.object_id AND
                ic.column_id = c.column_id
            WHERE
                t.schema_id = SCHEMA_ID()
            ORDER BY
                i.index_id,
                ic.index_column_id
        """
        )
        for table, index, unique, primary, type_, desc, order, column in cursor.fetchall():
            constraints.setdefault(table, {}).setdefault(
                index,
                {
                    'columns': [],
                    'is_primary_key': primary,
                    'is_unique': unique,
                    'foreign_key': None,
                    'is_check': False,
                    'is_index': True,
                    'orders': [],
                    'type': 'idx' if type_ in (1, 2) else desc.lower(),
                    'entity': 'index',
                },
            )
            # record the details
            constraints[table][index]['columns'].append(column)
            constraints[table][index]['orders'].append('DESC' if order == 1 else 'ASC')

        for table in constraints:
            constraints[table] = [{'name': k, **v} for k, v in constraints[table].items()]

        return constraints
