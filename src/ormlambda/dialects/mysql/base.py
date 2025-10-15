from __future__ import annotations
from types import ModuleType
from ormlambda import ColumnProxy, ForeignKey, TableProxy, Table, Column
from ormlambda.sql import compiler
from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.common.errors import NotKeysInIFunctionError
from ormlambda.sql.types import ASTERISK


from .. import default
from typing import TYPE_CHECKING, Any, Iterable, Type
from ormlambda.sql.comparer import Comparer, ComparerCluster

if TYPE_CHECKING:
    from ormlambda.sql.functions.interface import IFunction
    from ormlambda.sql.types import ColumnType
    from test.test_clause_info import ST_Contains
    from ormlambda import JoinSelector
    from ormlambda.sql.column.column import Column
    from mysql import connector
    from ormlambda.dialects.mysql.clauses import ST_AsText

from .types import (
    _NumericType,
    _NumericCommonType,
    _StringType,
    VARCHAR,
    CHAR,
    NUMERIC,
    DECIMAL,
    DOUBLE,
    REAL,
    FLOAT,
    INTEGER,
    BIGINT,
    MEDIUMINT,
    TINYINT,
    SMALLINT,
    BIT,
    TIME,
    TIMESTAMP,
    DATETIME,
    YEAR,
    TEXT,
    TINYTEXT,
    MEDIUMTEXT,
    LONGTEXT,
    NVARCHAR,
    NCHAR,
    TINYBLOB,
    MEDIUMBLOB,
    LONGBLOB,
)
from ormlambda.sql.sqltypes import (
    LARGEBINARY,
    BLOB,
    BOOLEAN,
    DATE,
    UUID,
    VARBINARY,
)
from .caster import MySQLCaster
from .repository import MySQLRepository


if TYPE_CHECKING:
    from ormlambda.sql.clauses import (
        Select,
        Insert,
        Delete,
        Upsert,
        Update,
        Limit,
        Offset,
        Where,
        Having,
        Order,
        GroupBy,
    )

    from ormlambda.sql.functions import (
        Max,
        Min,
        Concat,
        Sum,
        Count,
        Avg,
        Abs,
        Ceil,
        Floor,
        Round,
        Pow,
        Sqrt,
        Mod,
        Rand,
        Truncate,
    )


class MySQLCompiler(compiler.SQLCompiler):
    render_table_with_column_in_update_from = True
    """Overridden from base SQLCompiler value"""

    def visit_table_proxy(self, table: TableProxy, **kw) -> str:
        param = {
            "table": None,
            "column": table._table_class.__table_name__,
            "dialect": self.dialect,
            "alias_clause": alias if (alias := table.get_table_chain()) else None,
            **kw,
        }
        return ClauseInfo(**param).query(dialect=self.dialect)

    def visit_column(self, column: Column, **kw) -> str:
        params = {
            "table": column.table,
            "column": column.column_name,
            "dtype": column.dtype,
            "dialect": self.dialect,
            **kw,
        }
        return ClauseInfo(**params).query(self.dialect)

    def visit_column_proxy(self, column: ColumnProxy, **kw) -> str:
        from ormlambda.sql.clause_info import ClauseInfo

        alias_table = column.get_table_chain()

        params = {
            "table": column.table,
            "column": column,
            "alias_table": alias_table if alias_table else "{table}",
            "alias_clause": column.alias or "{column}",
            "dtype": column._column.dtype,
            "dialect": self.dialect,
            **kw,
        }
        clause_info = ClauseInfo(**params)
        if column.alias != clause_info.alias_clause:
            # FIXME [ ]: i don't understand why
            column.alias = clause_info.alias_clause
        return clause_info.query(self.dialect)

    def visit_comparer_cluster(self, cluster: ComparerCluster, **kw) -> str:
        c1 = cluster.left_comparer.compile(self.dialect, **kw).string
        c2 = cluster.right_comparer.compile(self.dialect, **kw).string

        return f"{c1} {cluster.join} {c2}"

    def visit_comparer(self, comparer: Comparer, **kwargs) -> str:
        from ormlambda.sql.comparer import CleanValue, Comparer

        def compile_condition(condition: Any):
            if isinstance(condition, ColumnProxy | Comparer):
                param = {
                    "alias_clause": None,
                    **kwargs,
                }
                return condition.compile(self.dialect, **param).string
            return MySQLCaster.cast(condition, type(condition)).string_data

        lcond = compile_condition(comparer.left_condition)
        rcond = compile_condition(comparer.right_condition)

        if comparer._flags:
            rcond = CleanValue(rcond, comparer._flags).clean()

        return f"{lcond} {comparer.compare} {rcond}"

    def visit_where(self, where: Where) -> str:
        assert (n := len(where.comparers)) == len(where.restrictive)

        if not where.comparers:
            return ""

        cond = []

        for i in range(n):
            comp = where.comparers[i]

            string = comp.compile(self.dialect).string

            condition = f"({string})" if isinstance(comp, ComparerCluster) else string

            union = f" {where.restrictive[i + 1]} " if i != n - 1 else ""

            condition += union
            cond.append(condition)
        return f" WHERE {"".join(cond)}"

    def visit_having(self, having: Having) -> str:
        assert (n := len(having.comparers)) == len(having.restrictive)

        if not having.comparers:
            return ""

        cond = []

        for i in range(n):
            comp = having.comparers[i]

            string = comp.compile(self.dialect).string

            condition = f"({string})" if isinstance(comp, ComparerCluster) else string

            union = f" {having.restrictive[i + 1]} " if i != n - 1 else ""

            condition += union
            cond.append(condition)
        return f" HAVING {"".join(cond)}"

    def visit_join(self, join: JoinSelector) -> str:
        rt = join.rcon.table
        rtable = TableProxy(table_class=rt, path=join.rcon.path)

        from_clause = rtable.compile(self.dialect, alias_clause=join.alias).string
        left_table_clause = join.lcon.compile(self.dialect, alias_clause=None).string
        right_table_clause = join.rcon.compile(self.dialect, alias_table=join.alias, alias_clause=None).string
        list_ = [
            join._by.value,  # inner join
            from_clause,
            "ON",
            left_table_clause,
            join._compareop,  # =
            right_table_clause,
        ]
        return " ".join([x for x in list_ if x is not None])

    def visit_select(self, select: Select):
        params = {}

        # COMMENT: when passing alias into 'select' method, we gonna replace the current aliases of columns with the generic one.
        # TODOM []: Check if we manage some conditions or not
        if select.avoid_duplicates:
            params["alias_clause"] = lambda x: x.get_full_chain("_")
        elif select.alias:
            params["alias_clause"] = select.alias

        columns = ClauseInfo.join_clauses(select.columns, ",", dialect=self.dialect, **params)
        from_ = ClauseInfo(
            select._table,
            None,
            alias_table=select._alias_table,
            dialect=self.dialect,
        ).query(self.dialect)

        return f"SELECT {columns} FROM {from_}"

    def visit_group_by(self, groupby: GroupBy):
        column = ", ".join(x.compile(self.dialect, alias_clause=None).string for x in groupby.column)
        return f"GROUP BY {column}"

    def visit_limit(self, limit: Limit, **kw):
        return f"LIMIT {limit._number}"

    # TODOH [x]: include the rest of visit methods
    def visit_insert[T, TProp](self, insert: Insert) -> str:
        def __is_valid[TProp](column: Column[TProp], value: TProp) -> bool:
            """
            We want to delete the column from table when it's specified with an 'AUTO_INCREMENT' or 'AUTO GENERATED ALWAYS AS (__) STORED' statement.

            if the column is auto-generated, it means the database creates the value for that column, so we must deleted it.
            if the column is primary key and auto-increment, we should be able to create an object with specific pk value.

            RETURN
            -----

            - True  -> Do not delete the column from dict query
            - False -> Delete the column from dict query
            """

            is_pk_none_and_auto_increment: bool = all([value is None, column.is_primary_key, column.is_auto_increment])

            if is_pk_none_and_auto_increment or column.is_auto_generated:
                return False
            return True

        def __fill_dict_list(list_dict: list[str, TProp], values: list[T]) -> list[Column]:
            if isinstance(values, Iterable):
                for x in values:
                    __fill_dict_list(list_dict, x)

            elif issubclass(values.__class__, Table):
                new_list = []
                for prop in type(values).__dict__.values():
                    if not isinstance(prop, Column):
                        continue

                    value = getattr(values, prop.column_name)
                    if __is_valid(prop, value):
                        new_list.append(prop)
                list_dict.append(new_list)

            else:
                raise Exception(f"Tipo de dato'{type(values)}' no esperado")
            return None

        if not isinstance(insert.values, Iterable):
            values = (insert.values,)
        else:
            values = insert.values
        valid_cols: list[list[Column]] = []
        __fill_dict_list(valid_cols, values)

        col_names: list[str] = []
        wildcards: list[str] = []
        col_values: list[list[str]] = []
        for i, cols in enumerate(valid_cols):
            col_values.append([])
            CASTER = self.dialect.caster()
            for col in cols:
                clean_data = CASTER.for_column(col, insert.values[i])  # .resolve(insert.values[i][col])
                if i == 0:
                    col_names.append(col.column_name)
                    wildcards.append(clean_data.wildcard_to_insert())
                # COMMENT: avoid MySQLWriteCastBase.resolve when using PLACEHOLDERs
                col_values[-1].append(clean_data.to_database)

        join_cols = ", ".join(col_names)
        unknown_rows = f"({', '.join(wildcards)})"  # The number of "%s" must match the dict 'dicc_0' length

        insert.cleaned_values = [tuple(x) for x in col_values]
        query = f"INSERT INTO {insert.table.__table_name__} {f'({join_cols})'} VALUES {unknown_rows}"
        return query

    def visit_delete(self, delete: Delete, **kw) -> str:
        return f"DELETE FROM {delete.table.__table_name__}"

    def visit_upsert(self, upsert: Upsert, **kw) -> str:
        """
        Generate MySQL UPSERT query using INSERT ... ON DUPLICATE KEY UPDATE.

        Works with both single dictionaries and lists of changes. The function only
        generates placeholders and column names - actual values are bound separately.

        Parameters
        ----------
        upsert : Upsert
            Upsert object containing table and values information

        Returns
        -------
        str
            SQL query string with placeholders

        Examples
        --------
        Generated SQL:
            INSERT INTO users (id, name, email)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                email = VALUES(email);

        Actual execution with bound values:
            [(1, 'Pablo', 'pablo@example.com'),
            (2, 'Marina', 'marina@example.com')]

        Notes
        -----
        - Primary key column is excluded from the UPDATE clause
        - Uses MySQL's VALUES() function to reference inserted values
        - For batch inserts, all rows must have the same column structure
        """

        # Generate the INSERT portion of the query
        query_insert = self.visit_insert(upsert)

        # MySQL uses VALUES() function to reference inserted values in UPDATE clause
        VALUES_FUNCTION = "VALUES"

        # Validate that we have values to work with
        if not upsert.values or len(upsert.values) == 0:
            raise ValueError("Upsert requires at least one value dictionary")

        # Get column information from first value (all rows should have same structure)
        first_value = upsert.values[0]
        columns = first_value.get_columns()
        pk_column = first_value.get_pk().column_name

        # Build UPDATE clause: exclude primary key from updates
        # Format: column = VALUES(column)
        # fmt: off
        update_columns = [
            f"{col} = {VALUES_FUNCTION}({col})" 
            for col in columns 
            if col != pk_column
        ]
        # fmt: on

        # Handle edge case: if only PK exists, nothing to update
        if not update_columns:
            raise ValueError(f"No columns to update besides primary key '{pk_column}'. " "UPSERT requires at least one non-PK column.")

        update_clause = ", ".join(update_columns)

        return f"{query_insert} ON DUPLICATE KEY UPDATE {update_clause};"

    def visit_update(self, update: Update, **kw) -> str:
        class UpdateKeyError(KeyError):
            def __init__(self, table: Type[Table], key: str | ColumnType, *args):
                super().__init__(*args)
                self._table: Type[Table] = table
                self._key: str | ColumnType = key

            def __str__(self):
                BASE_MSSG = lambda col: f"The column '{col}' does not belong to the table '{self._table.__table_name__}'"  # noqa: E731

                if isinstance(self._key, Column):
                    return BASE_MSSG(self._key.column_name) + f"; it belongs to the table '{self._key.table.__table_name__}'. Please check the columns in the query."
                return BASE_MSSG(self._key) + ". Please check the columns in the query."

        def __is_valid__(col: Column) -> bool:
            if update.table is not col.table:
                raise UpdateKeyError(update.table, col)
            return not col.is_auto_generated

        if not isinstance(update.values, dict):
            raise TypeError

        col_names: list[Column] = []
        CASTER = self.dialect.caster()
        for col, value in update.values.items():
            if isinstance(col, str):
                if not hasattr(update.table, col):
                    raise UpdateKeyError(update.table, col)
                col = getattr(update.table, col)
            if not isinstance(col, Column | ColumnProxy):
                raise ValueError

            if __is_valid__(col):
                clean_data = CASTER.for_value(value)
                col_names.append((col.column_name, clean_data.wildcard_to_insert()))
                update.cleaned_values.append(clean_data.to_database)

        set_query: str = ",".join(["=".join(col_data) for col_data in col_names])

        query = f"UPDATE {update.table.__table_name__} SET {set_query}"
        update.cleaned_values = tuple(update.cleaned_values)
        return query

    def visit_offset(self, offset: Offset, **kw) -> str:
        return f"OFFSET {offset._number}"

    def visit_count(self, count: Count, **kw) -> str:
        if isinstance(count.column, ColumnProxy):
            column = count.column.compile(self.dialect, alias_clause=None).string

        elif isinstance(count.column, TableProxy):
            column = ASTERISK

        else:
            column = count.column

        return ClauseInfo.concat_alias_and_column(f"COUNT({column})", count.alias)

    def visit_order(self, order: Order, **kw) -> str:
        ORDER = "ORDER BY"
        string_columns: list[str] = []
        columns = order.columns

        # if this attr is not iterable means that we only pass one column without wrapped in a list or tuple

        if not isinstance(columns, Iterable):
            columns = (columns,)

        assert len(columns) == len(order._order_type)

        for index, clause in enumerate(columns):
            # We need to avoid wrapped columns with `` or '' when clause hasn't table
            if isinstance(columns, str):
                string_columns = f"{columns} {str(order._order_type[0])}"
                return f"{ORDER} {string_columns}"

            if not clause.table:
                string_column = clause.compile(
                    self.dialect,
                    table=None,
                    alias_clause=None,
                    literal=True,
                ).string
            else:
                string_column = clause.compile(self.dialect, alias_clause=None).string

            string_columns.append(f"{string_column} {str(order._order_type[index])}")

        return f"{ORDER} {', '.join(string_columns)}"

    def visit_concat(self, concat: Concat, **kw) -> Concat:
        columns: list[str] = []

        for clause in concat.values:
            if isinstance(clause, ColumnProxy):
                compiled = clause.compile(self.dialect, alias_clause=None).string
            else:
                compiled = f"'{clause}'"
            columns.append(compiled)

        clause_info = ClauseInfo(
            table=None,
            column=f"CONCAT({', '.join(columns)})",
            alias_clause=concat.alias,
            dialect=self.dialect,
        )
        return clause_info.query(self.dialect)

    def visit_max(self, obj: Max, **kw) -> str:
        return self._compile_aggregate_method("MAX", obj, **kw)

    def visit_min(self, obj: Min, **kw) -> str:
        return self._compile_aggregate_method("MIN", obj, **kw)

    def visit_sum(self, obj: Sum, **kw) -> str:
        return self._compile_aggregate_method("SUM", obj, **kw)

    def visit_avg(self, obj: Avg, **kw) -> str:
        return self._compile_aggregate_method("AVG", obj, **kw)

    def visit_abs(self, obj: Abs, **kw) -> str:
        return self._compile_aggregate_method("ABS", obj, **kw)

    def visit_ceil(self, obj: Ceil, **kw) -> str:
        return self._compile_aggregate_method("CEIL", obj, **kw)

    def visit_floor(self, obj: Floor, **kw) -> str:
        return self._compile_aggregate_method("FLOOR", obj, **kw)

    def visit_round(self, obj: Round, **kw) -> str:
        return self._compile_aggregate_method("ROUND", obj, **kw)

    def visit_pow(self, obj: Pow, **kw) -> str:
        attr = {**kw, "alias_clause": None}
        column = obj.column.compile(self.dialect, **attr).string
        return ClauseInfo.concat_alias_and_column(f"POW({column}, {obj._exponent})", obj.alias)

    def visit_sqrt(self, obj: Sqrt, **kw) -> str:
        return self._compile_aggregate_method("SQRT", obj, **kw)

    def visit_mod(self, obj: Mod, **kw) -> str:
        attr = {**kw, "alias_clause": None}
        column = obj.column.compile(self.dialect, **attr).string
        return ClauseInfo.concat_alias_and_column(f"MOD({column}, {obj._divisor})", obj.alias)

    def visit_rand(self, obj: Rand, **kw) -> str:
        return self._compile_aggregate_method("RAND", obj, **kw)

    def visit_truncate(self, obj: Truncate, **kw) -> str:
        attr = {**kw, "alias_clause": None}
        column = obj.column.compile(self.dialect, **attr).string
        return ClauseInfo.concat_alias_and_column(f"TRUNCATE({column}, {obj._decimal})", obj.alias)

    def _compile_aggregate_method(self, name: str, function: IFunction, **kw) -> str:
        attr = {**kw, "alias_clause": None}
        column = function.column.compile(self.dialect, **attr).string
        return ClauseInfo.concat_alias_and_column(f"{name}({column})", function.alias)

    def visit_st_astext(self, st_astext: ST_AsText) -> str:
        # avoid use placeholder when using IFunction because no make sense.
        if st_astext.alias and (found := ClauseInfo._keyRegex.findall(st_astext.alias)):
            raise NotKeysInIFunctionError(found)
        return ClauseInfo.concat_alias_and_column(f"ST_AsText({st_astext.column.compile(self.dialect, alias_clause=None).string})", st_astext.alias)

    def visit_st_contains(self, st_contains: ST_Contains) -> str:
        attr1 = st_contains.column.compile(self.dialect, alias_clause=None).string
        attr2 = ClauseInfo(None, st_contains.point, dialect=self.dialect).query(self.dialect, alias_clause=None)
        return f"ST_Contains({attr1}, {attr2})"


class MySQLDDLCompiler(compiler.DDLCompiler):
    def get_column_specification(self, column: Column, **kwargs):
        colspec = column.column_name + " " + self.dialect.type_compiler_instance.process(column.dbtype)
        default = self.get_column_default_string(column)
        if default is not None:
            colspec += " DEFAULT " + default

        if column.is_not_null:
            colspec += " NOT NULL"

        if column.is_primary_key:
            colspec += " PRIMARY KEY"

        colspec += " AUTO_INCREMENT" if column.is_auto_increment else ""

        return colspec

    def visit_foreign_key(self, fk: ForeignKey, **kw) -> str:
        compare = fk.resolved_function()
        lcon = compare.left_condition
        rcon = compare.right_condition
        return f"FOREIGN KEY ({lcon.column_name}) REFERENCES {rcon.table.__table_name__}({rcon.column_name})"


class MySQLTypeCompiler(compiler.GenericTypeCompiler):
    def mysql_type(self, type_: Any) -> bool:
        return isinstance(type_, (_StringType, _NumericType))

    def _extend_numeric(self, type_: _NumericType, spec: str) -> str:
        "Extend a numeric-type declaration with MySQL specific extensions."

        if not self.mysql_type(type_):
            return spec

        if type_.unsigned:
            spec += " UNSIGNED"
        if type_.zerofill:
            spec += " ZEROFILL"
        return spec

    def _extend_string(self, type_: _StringType, defaults, spec):
        """Extend a string-type declaration with standard SQL CHARACTER SET /
        COLLATE annotations and MySQL specific extensions.

        """

        def attr(name):
            return getattr(type_, name, defaults.get(name))

        if attr("charset"):
            charset = f"CHARACTER SET {attr('charset')}"
        elif attr("ascii"):
            charset = "ASCII"
        elif attr("unicode"):
            charset = "UNICODE"
        else:
            charset = None

        if attr("collation"):
            collation = f"COLLATE {type_.collation}"
        elif attr("binary"):
            collation = "BINARY"
        else:
            collation = None

        if attr("national"):
            # NATIONAL (aka NCHAR/NVARCHAR) trumps charsets.
            return " ".join([c for c in ("NATIONAL", spec, collation) if c is not None])
        return " ".join([c for c in (spec, charset, collation) if c is not None])

    def _mysql_type(self, type_, **kw):
        return isinstance(type, _StringType | _NumericCommonType)

    def visit_NUMERIC(self, type_: NUMERIC, **kw):
        if type_.precision is None:
            return self._extend_numeric(type_, "NUMERIC")
        elif type_.scale is None:
            return self._extend_numeric(
                type_,
                f"NUMERIC({type_.precision})",
            )
        else:
            return self._extend_numeric(
                type_,
                f"NUMERIC({type_.precision}, {type_.scale})",
            )

    def visit_DECIMAL(self, type_: DECIMAL, **kw):
        if type_.precision is None:
            return self._extend_numeric(type_, "DECIMAL")
        elif type_.scale is None:
            return self._extend_numeric(
                type_,
                f"DECIMAL({type_.precision})",
            )
        else:
            return self._extend_numeric(
                type_,
                f"DECIMAL({type_.precision}, {type_.scale})",
            )

    def visit_DOUBLE(self, type_: DOUBLE, **kw):
        if type_.precision is not None and type_.scale is not None:
            return self._extend_numeric(
                type_,
                f"DOUBLE({type_.precision}, {type_.scale})",
            )
        else:
            return self._extend_numeric(type_, "DOUBLE")

    def visit_REAL(self, type_: REAL, **kw):
        if type_.precision is not None and type_.scale is not None:
            return self._extend_numeric(
                type_,
                f"REAL({type_.precision}, {type_.scale})",
            )
        else:
            return self._extend_numeric(type_, "REAL")

    def visit_FLOAT(self, type_: FLOAT, **kw):
        if self._mysql_type(type_) and type_.scale is not None and type_.precision is not None:
            return self._extend_numeric(type_, f"FLOAT({type_.precision}, {type_.scale})")
        elif type_.precision is not None:
            return self._extend_numeric(type_, f"FLOAT({type_.precision})")
        else:
            return self._extend_numeric(type_, "FLOAT")

    def visit_INTEGER(self, type_: INTEGER, **kw):
        if self._mysql_type(type_) and type_.display_width is not None:
            return self._extend_numeric(
                type_,
                f"INTEGER({type_.display_width})",
            )
        else:
            return self._extend_numeric(type_, "INTEGER")

    def visit_BIGINT(self, type_: BIGINT, **kw):
        if self._mysql_type(type_) and type_.display_width is not None:
            return self._extend_numeric(
                type_,
                f"BIGINT({type_.display_width})",
            )
        else:
            return self._extend_numeric(type_, "BIGINT")

    def visit_MEDIUMINT(self, type_: MEDIUMINT, **kw):
        if self._mysql_type(type_) and type_.display_width is not None:
            return self._extend_numeric(
                type_,
                f"MEDIUMINT({type_.display_width})",
            )
        else:
            return self._extend_numeric(type_, "MEDIUMINT")

    def visit_TINYINT(self, type_: TINYINT, **kw):
        if self._mysql_type(type_) and type_.display_width is not None:
            return self._extend_numeric(type_, f"TINYINT({type_.display_width})")
        else:
            return self._extend_numeric(type_, "TINYINT")

    def visit_SMALLINT(self, type_: SMALLINT, **kw):
        if self._mysql_type(type_) and type_.display_width is not None:
            return self._extend_numeric(
                type_,
                f"SMALLINT({type_.display_width})",
            )
        else:
            return self._extend_numeric(type_, "SMALLINT")

    def visit_BIT(self, type_: BIT, **kw):
        if type_.length is not None:
            return f"BIT({type_.length})"
        else:
            return "BIT"

    def visit_DATETIME(self, type_: DATETIME, **kw):
        if getattr(type_, "fsp", None):
            return f"DATETIME({type_.fsp})"
        else:
            return "DATETIME"

    def visit_DATE(self, type_: DATE, **kw):
        return "DATE"

    def visit_TIME(self, type_: TIME, **kw):
        if getattr(type_, "fsp", None):
            return f"TIME({type_.fsp})"
        else:
            return "TIME"

    def visit_TIMESTAMP(self, type_: TIMESTAMP, **kw):
        if getattr(type_, "fsp", None):
            return f"TIMESTAMP({type_.fsp})"
        else:
            return "TIMESTAMP"

    def visit_YEAR(self, type_: YEAR, **kw):
        if type_.display_width is None:
            return "YEAR"
        else:
            return f"YEAR({type_.display_width})"

    def visit_TEXT(self, type_: TEXT, **kw):
        if type_.length is not None:
            return self._extend_string(type_, {}, f"TEXT({type_.length})")
        else:
            return self._extend_string(type_, {}, "TEXT")

    def visit_TINYTEXT(self, type_: TINYTEXT, **kw):
        return self._extend_string(type_, {}, "TINYTEXT")

    def visit_MEDIUMTEXT(self, type_: MEDIUMTEXT, **kw):
        return self._extend_string(type_, {}, "MEDIUMTEXT")

    def visit_LONGTEXT(self, type_: LONGTEXT, **kw):
        return self._extend_string(type_, {}, "LONGTEXT")

    def visit_VARCHAR(self, type_: VARCHAR, **kw):
        if type_.length is not None:
            return self._extend_string(type_, {}, f"VARCHAR({type_.length})")
        else:
            raise ValueError(f"VARCHAR requires a length on dialect {self.dialect.name}")

    def visit_CHAR(self, type_: CHAR, **kw):
        if type_.length is not None:
            return self._extend_string(type_, {}, f"CHAR({type_.length})")
        else:
            return self._extend_string(type_, {}, "CHAR")

    def visit_NVARCHAR(self, type_: NVARCHAR, **kw):
        # We'll actually generate the equiv. "NATIONAL VARCHAR" instead
        # of "NVARCHAR".
        if type_.length is not None:
            return self._extend_string(
                type_,
                {"national": True},
                f"VARCHAR({type_.length})",
            )
        else:
            raise ValueError(f"NVARCHAR requires a length on dialect {self.dialect.name}")

    def visit_NCHAR(self, type_: NCHAR, **kw):
        # We'll actually generate the equiv.
        # "NATIONAL CHAR" instead of "NCHAR".
        if type_.length is not None:
            return self._extend_string(
                type_,
                {"national": True},
                f"CHAR({type_.length})",
            )
        else:
            return self._extend_string(type_, {"national": True}, "CHAR")

    def visit_UUID(self, type_: UUID, **kw):
        return "UUID"

    def visit_VARBINARY(self, type_: VARBINARY, **kw):
        return f"VARBINARY({type_.length})"

    def visit_JSON(self, type_, **kw):
        return "JSON"

    def visit_large_binary(self, type_: LARGEBINARY, **kw):
        return self.visit_BLOB(type_)

    def visit_enum(self, type_, **kw):
        if not type_.native_enum:
            return super().visit_enum(type_)
        else:
            return self.visit_ENUM(type_, type_.enums)

    def visit_BLOB(self, type_: BLOB, **kw):
        if type_.length is not None:
            return f"BLOB({type_.length})"
        else:
            return "BLOB"

    def visit_TINYBLOB(self, type_: TINYBLOB, **kw):
        return "TINYBLOB"

    def visit_MEDIUMBLOB(self, type_: MEDIUMBLOB, **kw):
        return "MEDIUMBLOB"

    def visit_LONGBLOB(self, type_: LONGBLOB, **kw):
        return "LONGBLOB"

    def _visit_enumerated_values(self, name, type_, enumerated_values):
        quoted_enums = []
        for e in enumerated_values:
            if self.dialect.identifier_preparer._double_percents:
                e = e.replace("%", "%%")
            quoted_enums.append(f"'{e.replace("'", "''")}'")
        return self._extend_string(type_, {}, f"{name}({','.join(quoted_enums)})")

    def visit_ENUM(self, type_, **kw):
        return self._visit_enumerated_values("ENUM", type_, type_.enums)

    def visit_SET(self, type_, **kw):
        return self._visit_enumerated_values("SET", type_, type_.values)

    def visit_BOOLEAN(self, type_: BOOLEAN, **kw):
        return "BOOL"


class MySQLDialect(default.DefaultDialect):
    """Details of the MySQL dialect.
    Not used directly in application code.
    """

    dbapi: connector
    name = "mysql"

    statement_compiler = MySQLCompiler
    ddl_compiler = MySQLDDLCompiler
    type_compiler_cls = MySQLTypeCompiler
    caster = MySQLCaster

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def import_dbapi(cls) -> ModuleType:
        from mysql import connector

        return connector

    @classmethod
    def get_pool_class(cls, url):
        return MySQLRepository
