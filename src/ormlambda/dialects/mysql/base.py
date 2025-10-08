from __future__ import annotations
from types import ModuleType
from ormlambda import ColumnProxy, ForeignKey, TableProxy
from ormlambda.sql import compiler
from ormlambda.sql.clause_info import ClauseInfo
from ormlambda.common.errors import NotKeysInIAggregateError
from ormlambda.sql.types import ASTERISK


from .. import default
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from test.test_clause_info import ST_Contains
    from ormlambda import JoinSelector
    from ormlambda.sql.comparer import Comparer
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

        elif isinstance(count.column, TableProxy):
            column = ASTERISK

        else:
            column = count.column

        return ClauseInfo.concat_alias_and_column(f"COUNT({column})", count.alias)

    def visit_where(self, where: Where) -> str:
        from ormlambda.sql.comparer import Comparer

        if not where.comparer:
            return ""
        cols = Comparer.join_comparers(list(where.comparer), restrictive=where.restrictive, dialect=self.dialect)
        return f"WHERE {cols}"

    def visit_having(self, having: Having) -> str:
        from ormlambda.sql.comparer import Comparer

        cols = Comparer.join_comparers(list(having.comparer), restrictive=having.restrictive, dialect=self.dialect, table=None, literal=True)
        return f"HAVING {cols}"

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

    def visit_max(self, max: Max, **kw) -> str:
        attr = {**kw, "alias_clause": None}
        column = max.column.compile(self.dialect, **attr).string
        return ClauseInfo.concat_alias_and_column(f"MAX({column})", max.alias)

    def visit_min(self, min: Min, **kw) -> str:
        attr = {**kw, "alias_clause": None}
        column = min.column.compile(self.dialect, **attr).string
        return ClauseInfo.concat_alias_and_column(f"MIN({column})", min.alias)

    def visit_sum(self, sum: Sum, **kw) -> str:
        attr = {**kw, "alias_clause": None}
        column = sum.column.compile(self.dialect, **attr).string
        return ClauseInfo.concat_alias_and_column(f"SUM({column})", sum.alias)

    def visit_st_astext(self, st_astext: ST_AsText) -> str:
        # avoid use placeholder when using IAggregate because no make sense.
        if st_astext.alias and (found := ClauseInfo._keyRegex.findall(st_astext.alias)):
            raise NotKeysInIAggregateError(found)
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
