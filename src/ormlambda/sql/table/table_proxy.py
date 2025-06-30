from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any, Type

from ormlambda.sql.column_table_proxy import ColumnTableProxy

if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.sql.context import FKChain
    from ormlambda import ForeignKey


type CurrentPathType = Optional[FKChain]
type ForeignKeyRegistryType = dict[str, list[ForeignKey]]
type PathAliasesType = dict[str, str]
type QueryMetadataType = dict[str, Any]


class TableProxy[T: Table](ColumnTableProxy):
    _table_class: Type[T]
    _path: FKChain

    def __init__(self, table_class: Type[T], path: FKChain):
        self._table_class = table_class
        super().__init__(path)

    def __repr__(self) -> str:
        return f"{TableProxy.__name__}({self._table_class.__table_name__}) Path={self._path.get_path_key()})"

    def __getattr__(self, name: str):
        """Intercept attribute access to handle foreign keys and columns"""

        from ormlambda import ColumnProxy
        from ormlambda.sql.foreign_key import ForeignKey
        from ormlambda import Column

        # Get the actual attribute from the table class
        try:
            attr = getattr(self._table_class, name)
        except AttributeError:
            raise AttributeError(f"'{self._table_class.__name__}' object has no attribute '{name}'")

        if isinstance(attr, ForeignKey):
            new_chain = attr._path
            return TableProxy(attr.tright, new_chain)

        elif isinstance(attr, Column):
            # Accessing a column - return column reference with path info
            return ColumnProxy(attr, self._path)

        else:
            return attr

    def get_path(self) -> FKChain:
        """Get the path that led to this table"""
        return self._path

    def get_alias(self) -> str:
        """Get the alias for this table based on its path"""
        return self._path.get_alias()


    def _get_full_reference(self):
        from ormlambda import ForeignKey

        alias: list[str] = [self._path.base.__table_name__]
        base = self._path.base

        n = len(self._path.steps)

        for i in range(n):
            attr = self._path.steps[i]

            # last element
            if i == n - 1:
                value = attr.column_name

            else:
                value = attr.clause_name
            alias.append(value)

        return ".".join(alias)
