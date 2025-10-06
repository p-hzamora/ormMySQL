from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any, Type

from ormlambda.sql.column_table_proxy import ColumnTableProxy
from ormlambda.sql.elements import ClauseElement
from ormlambda.sql.context import FKChain

from ormlambda import util

if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda import ForeignKey


type CurrentPathType = Optional[FKChain]
type ForeignKeyRegistryType = dict[str, list[ForeignKey]]
type PathAliasesType = dict[str, str]
type QueryMetadataType = dict[str, Any]


class TableProxy[T: Table](ColumnTableProxy, ClauseElement):
    __visit_name__ = "table_proxy"
    _table_class: Type[Table]
    _path: FKChain

    def __init__(self, table_class: Type[T], path: Optional[FKChain] = None):
        if not path:
            path = FKChain(table_class, [])

        self._table_class = table_class
        super().__init__(path.copy())

    def __repr__(self) -> str:
        return f"{TableProxy.__name__}({self._table_class.__table_name__}) Path={self._path.get_path_key()})"

    @util.preload_module(
        "ormlambda.sql.foreign_key",
        "ormlambda.sql.column",
    )
    def __getattr__(self, name: str):
        """Intercept attribute access to handle foreign keys and columns"""

        ColumnProxy = util.preloaded.sql_column.ColumnProxy
        Column = util.preloaded.sql_column.Column
        ForeignKey = util.preloaded.sql_foreign_key.ForeignKey

        # Get the actual attribute from the table class
        try:
            attr = getattr(self._table_class, name)
        except AttributeError:
            # If column doesn't exist is because we're dealing with aliases like
            #  `lambda x: x.count` where 'count' is actually an alias not a column name
            # we don't want use table name
            attr = Column(dtype=str)
            attr.column_name = name
            return ColumnProxy(attr, path=FKChain(None, []))

        if isinstance(attr, ForeignKey):
            new_path = self._path.copy()
            new_path.add_step(attr)
            return TableProxy(attr.tright, new_path)

        elif isinstance(attr, Column):
            # Accessing a column - return column reference with path info

            column = ColumnProxy(attr, self._path.copy())
            self._path.clear()
            return column

        else:
            return attr

    def get_alias(self) -> str:
        """Get the alias for this table based on its path"""
        return self._path.get_alias()

    def get_table_chain(self):
        return self.get_alias()

    @util.preload_module("ormlambda.sql.column")
    def get_columns(self) -> tuple[ColumnTableProxy]:
        ColumnProxy = util.preloaded.sql_column.ColumnProxy

        result = []
        for column in self._table_class.get_columns():
            col_proxy = ColumnProxy(column, self._path)
            result.append(col_proxy)
        return result
