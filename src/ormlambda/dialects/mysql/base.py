from __future__ import annotations
from types import ModuleType
from ormlambda import ColumnProxy
from ormlambda.sql import compiler
from ormlambda.sql.clause_info import AggregateFunctionBase

from .. import default
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
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

    def visit_column_proxy(self, column: ColumnProxy) -> str:
        return column.query(self.dialect)

    def visit_comparer(self, comparer: Comparer) -> str:
        return Comparer.join_comparers(
            comparer,
            dialect=self.dialect,
        )

    def visit_select(self, select: Select, **kw):
        return f"SELECT {select.COLUMNS} FROM {select.FROM.query(self.dialect, **kw)}"

    def visit_group_by(self, groupby: GroupBy, **kw):
        column = groupby._create_query(self.dialect, **kw)
        return f"GROUP BY {column}"

    def visit_limit(self, limit: Limit, **kw):
        return f"{limit.LIMIT} {limit._number}"

    # TODOH []: include the rest of visit methods
    def visit_insert(self, insert: Insert, **kw) -> Insert:
        pass

    def visit_delete(self, delete: Delete, **kw) -> Delete:
        pass

    def visit_upsert(self, upsert: Upsert, **kw) -> Upsert:
        pass

    def visit_update(self, update: Update, **kw) -> Update:
        pass

    def visit_offset(self, offset: Offset, **kw) -> Offset:
        return f"{offset.OFFSET} {offset._number}"

    def visit_count(self, count: Count, **kw) -> Count:
        if isinstance(count.column, ColumnProxy):
            alias = f"`{count.column.get_table_chain()}`"
            column = f"{alias}.{count.column.column_name}"
        else:
            column = count.column

        return f"COUNT({column}) AS {count.alias}"

    def visit_where(self, where: Where, **kw) -> Where:
        from ormlambda.sql.comparer import Comparer

        def join_condition(cls, wheres: Iterable[Where], restrictive: bool) -> str:
            if not isinstance(wheres, Iterable):
                wheres = (wheres,)

            comparers: list[Comparer] = []
            for where in wheres:
                for c in where._comparer:
                    comparers.append(c)
            return cls(*comparers, restrictive=restrictive).query(dialect=self.dialect)

        if isinstance(where._comparer, Iterable):
            comparer = Comparer.join_comparers(
                where._comparer,
                restrictive=where._restrictive,
                dialect=self.dialect,
            )
        else:
            comparer = where._comparer
        return f"WHERE {comparer}"

    def visit_having(self, having: Having, **kw) -> Having:
        pass

    def visit_order(self, order: Order, **kw) -> Order:
        string_columns: list[str] = []
        columns = order.columns

        # if this attr is not iterable means that we only pass one column without wrapped in a list or tuple
        if isinstance(columns, str):
            string_columns = f"{columns} {str(order._order_type[0])}"
            return f"{order.FUNCTION_NAME()} {string_columns}"

        if not isinstance(columns, Iterable):
            columns = (columns,)

        assert len(columns) == len(order._order_type)

        for index, clause in enumerate(AggregateFunctionBase._convert_into_clauseInfo(columns, dialect=self.dialect)):
            clause.alias_clause = None
            string_columns.append(f"{clause.query(self.dialect, **kw)} {str(order._order_type[index])}")

        return f"{order.FUNCTION_NAME()} {', '.join(string_columns)}"

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
