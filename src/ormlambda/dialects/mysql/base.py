from __future__ import annotations
from types import ModuleType
from ormlambda.sql import compiler
from .. import default
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
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


from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext


class MySQLCompiler(compiler.SQLCompiler):
    render_table_with_column_in_update_from = True
    """Overridden from base SQLCompiler value"""

    def visit_select(self, select: Select, **kw):
        return f"{select.CLAUSE} {select.COLUMNS} FROM {select.FROM.query(self.dialect, **kw)}"

    def visit_group_by(self, groupby: GroupBy, **kw):
        column = groupby._create_query(self.dialect, **kw)
        return f"{groupby.FUNCTION_NAME()} {column}"

    def visit_limit(self, limit: Limit, **kw):
        return f"{limit.LIMIT} {limit._number}"

    # TODOH []: include the rest of visit methods
    def visit_insert(self, insert: Insert, **kw) -> Insert: ...
    def visit_delete(self, delete: Delete, **kw) -> Delete: ...
    def visit_upsert(self, upsert: Upsert, **kw) -> Upsert: ...
    def visit_update(self, update: Update, **kw) -> Update: ...
    def visit_offset(self, offset: Offset, **kw) -> Offset:
        return f"{offset.OFFSET} {offset._number}"

    def visit_count(self, count: Count, **kw) -> Count: ...
    def visit_where(self, where: Where, **kw) -> Where: ...
    def visit_having(self, having: Having, **kw) -> Having: ...
    def visit_order(self, order: Order, **kw) -> Order:
        string_columns: list[str] = []
        columns = order.unresolved_column

        # if this attr is not iterable means that we only pass one column without wrapped in a list or tuple
        if isinstance(columns, str):
            string_columns = f"{columns} {str(order._order_type[0])}"
            return f"{order.FUNCTION_NAME()} {string_columns}"

        if not isinstance(columns, Iterable):
            columns = (columns,)

        assert len(columns) == len(order._order_type)

        context = ClauseInfoContext(table_context=order._context._table_context, clause_context=None) if order._context else None
        for index, clause in enumerate(order._convert_into_clauseInfo(columns, context, dialect=self.dialect)):
            clause.alias_clause = None
            string_columns.append(f"{clause.query(self.dialect, **kw)} {str(order._order_type[index])}")

        return f"{order.FUNCTION_NAME()} {', '.join(string_columns)}"

    def visit_concat(self, concat: Concat, **kw) -> Concat:
        from ormlambda.sql.clause_info import ClauseInfo

        columns: list[str] = []

        context = ClauseInfoContext(table_context=concat._context._table_context, clause_context=None) if concat._context else None

        for clause in concat._convert_into_clauseInfo(concat.unresolved_column, context=context, dialect=self.dialect):
            clause.alias_clause = concat.alias_clause
            columns.append(clause)
        return concat._concat_alias_and_column(f"CONCAT({ClauseInfo.join_clauses(columns, dialect=self.dialect)})", concat._alias_aggregate)

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

    # region visit lowercase

    def visit_integer(self, type_: INTEGER, **kw):
        return self.visit_INTEGER(type_, **kw)

    def visit_varchar(self, type_, **kw):
        return self.visit_VARCHAR(type_, **kw)

    def visit_char(self, type_, **kw):
        return self.visit_CHAR(type_, **kw)

    def visit_numeric(self, type_: NUMERIC, **kw):
        return self.visit_NUMERIC(type_, **kw)

    def visit_decimal(self, type_: DECIMAL, **kw):
        return self.visit_DECIMAL(type_, **kw)

    def visit_double(self, type_: DOUBLE, **kw):
        return self.visit_DOUBLE(type_, **kw)

    def visit_real(self, type_: REAL, **kw):
        return self.visit_REAL(type_, **kw)

    def visit_float(self, type_: FLOAT, **kw):
        return self.visit_FLOAT(type_, **kw)

    def visit_bigint(self, type_: BIGINT, **kw):
        return self.visit_BIGINT(type_, **kw)

    def visit_mediumint(self, type_: MEDIUMINT, **kw):
        return self.visit_MEDIUMINT(type_, **kw)

    def visit_tinyint(self, type_: TINYINT, **kw):
        return self.visit_TINYINT(type_, **kw)

    def visit_smallint(self, type_: SMALLINT, **kw):
        return self.visit_SMALLINT(type_, **kw)

    def visit_bit(self, type_: BIT, **kw):
        return self.visit_BIT(type_, **kw)

    def visit_time(self, type_: TIME, **kw):
        return self.visit_TIME(type_, **kw)

    def visit_timestamp(self, type_: TIMESTAMP, **kw):
        return self.visit_TIMESTAMP(type_, **kw)

    def visit_datetime(self, type_: DATETIME, **kw):
        return self.visit_DATETIME(type_, **kw)

    def visit_year(self, type_: YEAR, **kw):
        return self.visit_YEAR(type_, **kw)

    def visit_text(self, type_: TEXT, **kw):
        return self.visit_TEXT(type_, **kw)

    def visit_tinytext(self, type_: TINYTEXT, **kw):
        return self.visit_TINYTEXT(type_, **kw)

    def visit_mediumtext(self, type_: MEDIUMTEXT, **kw):
        return self.visit_MEDIUMTEXT(type_, **kw)

    def visit_longtext(self, type_: LONGTEXT, **kw):
        return self.visit_LONGTEXT(type_, **kw)

    def visit_nvarchar(self, type_: NVARCHAR, **kw):
        return self.visit_NVARCHAR(type_, **kw)

    def visit_nchar(self, type_: NCHAR, **kw):
        return self.visit_NCHAR(type_, **kw)

    def visit_tinyblob(self, type_: TINYBLOB, **kw):
        return self.visit_TINYBLOB(type_, **kw)

    def visit_mediumblob(self, type_: MEDIUMBLOB, **kw):
        return self.visit_MEDIUMBLOB(type_, **kw)

    def visit_longblob(self, type_: LONGBLOB, **kw):
        return self.visit_LONGBLOB(type_, **kw)

    # endregion


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
