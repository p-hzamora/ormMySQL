from __future__ import annotations
import threading
from contextlib import contextmanager
from typing import Callable, TYPE_CHECKING, Optional, Any, Type, overload, Protocol
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda import Column

if TYPE_CHECKING:
    from ormlambda.sql.comparer import Comparer
    from ormlambda import Table
    from ormlambda.sql.clause_info.clause_info_context import ClauseContextType


class LocalContext(Protocol):
    current_path: ForeignKeyPath


class ForeignKeyPath:
    steps: list[str]

    def __init__(self, steps: list[str]):
        self.steps = steps

    def __repr__(self):
        return self.get_path_key()

    def add_step(self, step_name: str):
        """Add a step to the path"""
        self.steps.append(step_name)

    def copy(self) -> ForeignKeyPath:
        return ForeignKeyPath(steps=self.steps.copy())

    def get_path_key(self) -> str:
        return self._generate_chain("->")

    def _generate_chain(self, char: str) -> str:
        return char.join(self.steps)

    def get_alias(self) -> str:
        """Generate table alias from the path"""
        return self._generate_chain("_") if self.steps else "base"


class PathContext:
    def __init__(self):
        self._local: Optional[LocalContext] = threading.local()
        self._local.current_path = None

    def get_current_path(self) -> Optional[ForeignKeyPath]:
        return self._local.current_path

    def set_current_path(self, path: ForeignKeyPath) -> None:
        self._local.current_path = path
        return None

    def clear_path(self):
        """Clear the current path"""
        if hasattr(self._local, "current_path"):
            delattr(self._local, "current_path")

    @contextmanager
    def path_context(self, initial_table: Optional[str] = None):
        old_path = self.get_current_path()
        new_path = ForeignKeyPath()
        if initial_table:
            new_path.add_step(initial_table)
        self.set_current_path(new_path)
        try:
            yield new_path
        finally:
            if old_path:
                self.set_current_path(old_path)
            else:
                self.clear_path()


_path_context = PathContext()


class ForeignKeyContext:
    def __init__(self):
        self.path_to_foreignkeys: dict[str, list[ForeignKey]] = {}
        self.foreignkey_to_paths: dict[ForeignKey, list[str]] = {}
        self.all_foreign_keys: set = set()

    def add_foreign_key_with_paths(self, foreign_key: ForeignKey, path: ForeignKeyPath):
        self.all_foreign_keys.add(foreign_key)
        path_key = path.get_path_key()

        # Map path to foreign keys
        if path_key not in self.path_to_foreignkeys:
            self.path_to_foreignkeys[path_key] = []

        self.path_to_foreignkeys[path_key].append(foreign_key)

        # Map foreign key to paths
        if foreign_key not in self.foreignkey_to_paths:
            self.foreignkey_to_paths[foreign_key] = []
        self.foreignkey_to_paths[foreign_key].append(path_key)

    def get_foreign_keys_for_path(self, path_key: str) -> list[ForeignKey]:
        return self.path_to_foreignkeys.get(path_key, [])

    def get_paths_for_foreign_key(self, foreign_key: ForeignKey) -> list[str]:
        """Get all paths through which a foreign key was accessed"""
        return self.foreignkey_to_paths.get(foreign_key, [])

    def get_all_paths(self) -> list[str]:
        """Get all unique paths that were tracked"""
        return list(self.path_to_foreignkeys.keys())

    def get_path_aliases(self) -> dict[str, str]:
        """Get mapping of paths to their generated aliases"""
        return {path_key: ForeignKeyPath(steps=path_key.split("->")).get_alias() for path_key in self.path_to_foreignkeys.keys()}

    def clear(self):
        """Clear all tracked data"""
        self.path_to_foreignkeys.clear()
        self.foreignkey_to_paths.clear()
        self.all_foreign_keys.clear()


class ForeignKey[TLeft: Table, TRight: Table](IQuery):
    @overload
    def __new__[LProp, RProp](self, comparer: Comparer[LProp, RProp], clause_name: str) -> None: ...
    @overload
    def __new__[LProp, TRight, RProp](cls, tright: Type[TRight], relationship: Callable[[TLeft, TRight], Any | Comparer[TLeft, LProp, TRight, RProp]], keep_alive: bool = ...) -> TRight: ...

    def __new__[LProp, TRight, RProp](
        cls,
        tright: Optional[TRight] = None,
        relationship: Optional[Callable[[TLeft, TRight], Any | Comparer[TLeft, LProp, TRight, RProp]]] = None,
        *,
        comparer: Optional[Comparer] = None,
        clause_name: Optional[str] = None,
        keep_alive: bool = False,
    ) -> TRight:
        return super().__new__(cls)

    def __init__[LProp, RProp](
        self,
        tright: Optional[TRight] = None,
        relationship: Optional[Callable[[TLeft, TRight], Any | Comparer[TLeft, LProp, TRight, RProp]]] = None,
        *,
        comparer: Optional[Comparer] = None,
        clause_name: Optional[str] = None,
        keep_alive: bool = False,
    ) -> None:
        self._keep_alive = keep_alive
        if comparer is not None and clause_name is not None:
            self.__init__with_comparer(comparer, clause_name)
        else:
            self.__init_with_callable(tright, relationship)

        # Global storage for tracking foreign key access
        self.stored_calls = ForeignKeyContext()

    def __init__with_comparer[LProp, RProp](self, comparer: Comparer[LProp, RProp], clause_name: str) -> None:
        self._relationship = None
        self._tleft: TLeft = comparer.left_condition.table
        self._tright: TRight = comparer.right_condition.table
        self._clause_name: str = clause_name
        self._comparer: Comparer[LProp, RProp] = comparer

    def __init_with_callable[LProp, RProp](self, tright: Optional[TRight], relationship: Optional[Callable[[TLeft, TRight], Comparer[LProp, RProp]]]) -> None:
        self._relationship: Callable[[TLeft, TRight], Comparer[LProp, RProp]] = relationship
        self._tleft: TLeft = None
        self._tright: TRight = tright
        self._clause_name: str = None
        self._comparer: Optional[Comparer] = None

    def __set_name__(self, owner: TLeft, name) -> None:
        self._tleft: TLeft = owner
        self._clause_name: str = name

    def __get__(self, obj: Optional[TRight], objtype=None) -> ForeignKey[TLeft, TRight] | TRight:
        if not obj:
            return self

        current_path = _path_context.get_current_path()
        if not current_path:
            raise RuntimeError(f"{ForeignKey.__name__} '{self._clause_name}' accessed outside of path context. Must be used within a query context.")
        new_path = current_path.copy()
        step_name = f"{self._tleft}_{self.clause_name}"
        new_path.add_step(step_name)

        self.stored_calls.add_foreign_key_with_paths(self, new_path)
        return TableProxy(self._tright)

    def __set__(self, obj, value):
        raise AttributeError(f"The {ForeignKey.__name__} '{self._clause_name}' in the '{self._tleft.__table_name__}' table cannot be overwritten.")

    def __getattr__(self, name: str):
        if self._tright is None:
            raise AttributeError("No right table assigned to ForeignKey")
        return getattr(self._tright, name)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(left={self._tleft.__name__ if self._tleft else 'None'}, right={self._tright.__name__ if self._tright else 'None'}, name={self._clause_name})"

    @property
    def tleft(self) -> TLeft:
        return self._tleft

    @property
    def tright(self) -> TRight:
        return self._tright

    @property
    def clause_name(self) -> str:
        return self._clause_name

    @property
    def query(self) -> str:
        compare = self.resolved_function()
        left_col = compare.left_condition.column
        rcon = alias if (alias := compare.right_condition.alias_table) else compare.right_condition.table.__table_name__
        return f"FOREIGN KEY ({left_col}) REFERENCES {rcon}({compare.right_condition.column})"

    @property
    def alias(self) -> str:
        self._comparer = self.resolved_function()
        lcol = self._comparer.left_condition._column.column_name
        rcol = self._comparer.right_condition._column.column_name
        return f"{self.tleft.__table_name__}_{lcol}_{rcol}"

    @classmethod
    def create_query(cls, orig_table: Table) -> list[str]:
        clauses: list[str] = []

        for attr in orig_table.__dict__.values():
            if isinstance(attr, ForeignKey):
                clauses.append(attr.query)
        return clauses

    def resolved_function[LProp: Any, RProp: Any](self, context: ClauseContextType = None) -> Comparer[LProp, RProp]:
        """ """
        if self._comparer is not None:
            return self._comparer

        left = self._tleft
        right = self._tright
        comparer = self._relationship(left, right)
        comparer.set_context(context)
        return comparer


class TableProxy:
    _table_class: Table
    _path: ForeignKeyPath

    def __init__(self, table_class: Table, path: ForeignKeyPath):
        self._table_class = table_class
        self._path = path
        self._table_instance = None

    def _get_table_instance(self):
        """Lazy creation of table instance"""
        if self._table_instance is None:
            self._table_instance = self._table_class()
        return self._table_instance

    def __getattr__(self, name: str):
        """Intercept attribute access to handle foreign keys and columns"""
        table_instance = self._get_table_instance()
        attr = getattr(table_instance, name)

        if isinstance(attr, ForeignKey):
            # Accessing another foreign key - update context and let FK handle it
            old_path = _path_context.get_current_path()
            _path_context.set_current_path(self._path)
            try:
                result = attr.__get__(None, self._table_class)
                return result
            finally:
                if old_path:
                    _path_context.set_current_path(old_path)
                else:
                    _path_context.clear_path()

        elif hasattr(attr, "__class__") and "Column" in str(attr.__class__):
            # Accessing a column - return column reference with path info
            return Column(self._table_class.__table_name__, name, self._path)

        else:
            # Regular attribute
            return attr

    def get_path(self) -> ForeignKeyPath:
        """Get the path that led to this table"""
        return self._path

    def get_alias(self) -> str:
        """Get the alias for this table based on its path"""
        return self._path.get_alias()

    def __repr__(self):
        return f"TableProxy({self._table_class.__table_name__}, path={self._path.get_path_key()})"
