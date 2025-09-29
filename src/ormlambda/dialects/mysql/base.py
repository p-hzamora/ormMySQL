from __future__ import annotations
from types import ModuleType
from ormlambda import ColumnProxy
from ormlambda.sql import compiler
from ormlambda.sql.clause_info import ClauseInfo

from .. import default
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from ormlambda import JoinSelector
    from ormlambda.sql.comparer import Comparer
    from ormlambda.sql.column.column import Column
    from mysql import connector

from .types import (
    _NumericType,
    _StringType,
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
from ormlambda.sql.sqltypes import BLOB

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
        Count,
        Where,
        Having,
        Order,
        GroupBy,
    )

    from ormlambda.sql.functions import (
        Concat,
        Max,
        Min,
        Sum,
    )


class MySQLCompiler(compiler.SQLCompiler):
    render_table_with_column_in_update_from = True
    """Overridden from base SQLCompiler value"""

    def visit_table_proxy(self, table: TableProxy, **kw) -> str:
        return ClauseInfo(
            table=None,
            column=table._table_class.__table_name__,
            dialect=self.dialect,
            **kw,
        ).query(dialect=self.dialect)

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
        return column.query(self.dialect, **kw)

    def visit_comparer(self, comparer: Comparer, **kwargs) -> str:
        from ormlambda.sql.comparer import CleanValue

        lcond = comparer.left_condition(self.dialect, **kwargs)
        rcond = comparer.right_condition(self.dialect, **kwargs)

        if comparer._flags:
            rcond = CleanValue(rcond, comparer._flags).clean()

        return f"{lcond} {comparer.compare} {rcond}"

    def visit_join(self,join:JoinSelector)->str:
        from_clause = join.right_table.compile(alias_table=join.alias, dialect=self.dialect)
        left_table_clause = join.left_table.compile(column=join.left_col, alias_table=join.lcon.alias_table, dialect=self.dialect)
        right_table_clause = join.right_table.compile(column=join.right_col, alias_table=join.alias, dialect=self.dialect)
        list_ = [
            join._by.value,  # inner join
            from_clause.compile(self.dialect),
            "ON",
            left_table_clause.compile(self.dialect),
            join._compareop,  # =
            right_table_clause.compile(self.dialect),
        ]
        return " ".join([x for x in list_ if x is not None])


    def visit_select(self, select: Select, **kw):
        return f"SELECT {select.COLUMNS} FROM {select.FROM.query(self.dialect, **kw)}"

    def visit_group_by(self, groupby: GroupBy):
        column = " ".join(x.compile(self.dialect, alias_clause=None).string for x in groupby.column)
        return f"GROUP BY {column}"

    def visit_limit(self, limit: Limit, **kw):
        return f"LIMIT {limit._number}"

    # TODOH []: include the rest of visit methods
    def visit_insert(self, insert: Insert, **kw) -> str:
        pass

    def visit_delete(self, delete: Delete, **kw) -> str:
        pass

    def visit_upsert(self, upsert: Upsert, **kw) -> str:
        pass

    def visit_update(self, update: Update, **kw) -> str:
        pass

    def visit_offset(self, offset: Offset, **kw) -> str:
        return f"OFFSET {offset._number}"

    def visit_count(self, count: Count, **kw) -> str:
        if isinstance(count.column, ColumnProxy):
            column = count.column.compile(self.dialect, alias_clause=None).string

        else:
            column = count.column

        return f"COUNT({column}) AS {count.alias}"

    def visit_where(self, where: Where) -> str:
        from ormlambda.sql.comparer import Comparer

        cols = Comparer.join_comparers(list(where.comparer), True, dialect=self.dialect)
        return f"WHERE {cols}"

    def visit_having(self, having: Having) -> str:
        from ormlambda.sql.comparer import Comparer

        cols = Comparer.join_comparers(list(having.comparer), True, dialect=self.dialect, table=None, literal=True)
        return f"HAVING {cols}"

    def visit_order(self, order: Order, **kw) -> str:
        ORDER = 'ORDER BY'
        string_columns: list[str] = []
        columns = order.columns

        # if this attr is not iterable means that we only pass one column without wrapped in a list or tuple
        if isinstance(columns, str):
            string_columns = f"{columns} {str(order._order_type[0])}"
            return f"{ORDER} {string_columns}"

        if not isinstance(columns, Iterable):
            columns = (columns,)

        assert len(columns) == len(order._order_type)

        for index, clause in enumerate(columns):
            # We need to avoid wrapped columns with `` or '' when clause hasn't table

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
        from ormlambda.sql.clause_info import ClauseInfo

        columns: list[str] = []

        new_cols = concat.join_elements()
        for clause in AggregateFunctionBase._convert_into_clauseInfo(new_cols, dialect=self.dialect):
            clause.alias_clause = concat.alias_clause
            columns.append(clause)
        return concat._concat_alias_and_column(f"CONCAT({ClauseInfo.join_clauses(columns, dialect=self.dialect)})", concat.alias)

    def visit_max(self, max: Max, **kw) -> Max: ...
    def visit_min(self, min: Min, **kw) -> Min: ...
    def visit_sum(self, sum: Sum, **kw) -> Sum: ...


class MySQLDDLCompiler(compiler.DDLCompiler):
    def get_column_specification(self, column: Column, **kwargs):
        colspec = column.column_name + " " + self.dialect.type_compiler_instance.process(column.dtype)
        default = self.get_column_default_string(column)
        if default is not None:
            colspec += " DEFAULT " + default

        if column.is_not_null:
            colspec += " NOT NULL"

        if column.is_primary_key:
            colspec += " PRIMARY KEY"

        colspec += " AUTO_INCREMENT" if column.is_auto_increment else ""

        return colspec


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

    def visit_INTEGER(self, type_: INTEGER, **kw):
        if self.mysql_type(type_) and type_.display_width is not None:
            return self._extend_numeric(
                type_,
                f"INTEGER(%({type_.display_width})s)",
            )
        else:
            return self._extend_numeric(type_, "INTEGER")

    def visit_VARCHAR(self, type_, **kw):
        if type_.length is None:
            raise ValueError("VARCHAR requires a length on dialect %s" % self.dialect.name)
        return self._extend_string(type_, {}, "VARCHAR(%d)" % type_.length)

    def visit_CHAR(self, type_, **kw):
        if type_.length is not None:
            return self._extend_string(type_, {}, "CHAR(%(length)s)" % {"length": type_.length})
        else:
            return self._extend_string(type_, {}, "CHAR")

    def visit_NUMERIC(self, type_: NUMERIC, **kw):
        return "NUMERIC"

    def visit_DECIMAL(self, type_: DECIMAL, **kw):
        return "DECIMAL"

    def visit_DOUBLE(self, type_: DOUBLE, **kw):
        return "DOUBLE"

    def visit_REAL(self, type_: REAL, **kw):
        return "REAL"

    def visit_FLOAT(self, type_: FLOAT, **kw):
        return "FLOAT"

    def visit_BIGINT(self, type_: BIGINT, **kw):
        return "BIGINT"

    def visit_MEDIUMINT(self, type_: MEDIUMINT, **kw):
        return "MEDIUMINT"

    def visit_TINYINT(self, type_: TINYINT, **kw):
        return "TINYINT"

    def visit_SMALLINT(self, type_: SMALLINT, **kw):
        return "SMALLINT"

    def visit_BIT(self, type_: BIT, **kw):
        return "BIT"

    def visit_TIME(self, type_: TIME, **kw):
        return "TIME"

    def visit_TIMESTAMP(self, type_: TIMESTAMP, **kw):
        return "TIMESTAMP"

    def visit_DATETIME(self, type_: DATETIME, **kw):
        return "DATETIME"

    def visit_YEAR(self, type_: YEAR, **kw):
        return "YEAR"

    def visit_TEXT(self, type_: TEXT, **kw):
        if type_.length is not None:
            return self._extend_string(type_, {}, f"TEXT({type_.length})")
        return self._extend_string(type_, {}, "TEXT")

    def visit_TINYTEXT(self, type_: TINYTEXT, **kw):
        return "TINYTEXT"

    def visit_MEDIUMTEXT(self, type_: MEDIUMTEXT, **kw):
        return "MEDIUMTEXT"

    def visit_LONGTEXT(self, type_: LONGTEXT, **kw):
        return "LONGTEXT"

    def visit_NVARCHAR(self, type_: NVARCHAR, **kw):
        return "NVARCHAR"

    def visit_NCHAR(self, type_: NCHAR, **kw):
        return "NCHAR"

    def visit_TINYBLOB(self, type_: TINYBLOB, **kw):
        return "TINYBLOB"

    def visit_BLOB(self, type_: BLOB, **kw) -> str:
        blob = "BLOB"
        blob += f"({type_.length})" if type_.length is not None else ""
        return blob

    def visit_MEDIUMBLOB(self, type_: MEDIUMBLOB, **kw):
        return "MEDIUMBLOB"

    def visit_LONGBLOB(self, type_: LONGBLOB, **kw):
        return "LONGBLOB"


class MySQLDialect(default.DefaultDialect):
    """Details of the MySQL dialect.
    Not used directly in application code.
    """

    dbapi: connector
    name = "mysql"

    statement_compiler = MySQLCompiler
    ddl_compiler = MySQLDDLCompiler
    type_compiler_cls = MySQLTypeCompiler
    repository_cls = MySQLRepository
    caster = MySQLCaster

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def import_dbapi(cls) -> ModuleType:
        from mysql import connector

        return connector
