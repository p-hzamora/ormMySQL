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
    BINARY,
)


from ormlambda.databases.my_sql import MySQLRepository, MySQLCaster


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

    def visit_concat(self, concat: Concat, **kw) -> Concat: ...
    def visit_max(self, max: Max, **kw) -> Max: ...
    def visit_min(self, min: Min, **kw) -> Min: ...
    def visit_sum(self, sum: Sum, **kw) -> Sum: ...


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
    repository_cls = MySQLRepository
    caster = MySQLCaster

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def import_dbapi(cls) -> ModuleType:
        from mysql import connector

        return connector
