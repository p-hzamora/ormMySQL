from __future__ import annotations
import threading
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator, Literal, Optional, Any, TypedDict, Protocol


if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.sql import ForeignKey
    from ormlambda.sql.context import FKChain
    from ormlambda.sql.clauses import JoinSelector

type CurrentPathType = FKChain
type ForeignKeyRegistryType = dict[str, ForeignKey]
type QueryMetadataType = dict[str, Any]
type TableAliasType = dict[str, str]  # table_name -> alias
type ClauseAliasType = dict[str, str]  # clause_key -> alias
type JoinSelectorType = dict[str, str]  # clause_key -> alias

# Separate persistent and transient data types
type PersistentDataKeys = Literal["foreign_key_registry"]
type ContextDictKeys = Literal[
    "current_path",
    "foreign_key_registry",
    "query_metadata",
    "table_aliases",
    "join_selector",
]


class ContextDict(TypedDict):
    current_path: CurrentPathType
    foreign_key_registry: ForeignKeyRegistryType  # PERSISTENT: Survives across queries
    query_metadata: QueryMetadataType  # TRANSIENT: Reset per query
    table_aliases: TableAliasType  # TRANSIENT: Reset per query
    join_selector: JoinSelectorType  # TRANSIENT: Reset per query


class LocalContext(Protocol):
    context: ContextDict


class PathContext:
    _local: LocalContext

    def __init__(self):
        self._local = threading.local()

    def __repr__(self):
        return f"{PathContext.__name__}"

    @staticmethod
    def _initialize_context() -> ContextDict:
        return {
            "current_path": NO_CURRENT_PATH,
            "foreign_key_registry": {},
            "query_metadata": {},
            "table_aliases": {},
            "join_selector": {},
        }

    def _get_context(self, key: Optional[ContextDictKeys] = None) -> ContextDict:
        """
        we Always need to return the context variable itself to has a references to the context variable.
        An approach like return self._initialize_context() won't work as expected
        """
        if not self.has_context():
            self._set_context(self._initialize_context())

        return self._local.context if not key else self._local.context.get(key, None)

    def _set_context(self, context: ContextDict) -> None:
        self._local.context = context
        return None

    def get_current_path(self) -> Optional[FKChain]:
        return self._get_context("current_path")

    def set_current_path(self, path: FKChain) -> None:
        context = self._get_context()
        context["current_path"] = path
        return None

    def add_foreign_key_access(self, fk: ForeignKey, path: FKChain) -> None:
        context = self._get_context()

        # Store in registry
        if fk not in context["foreign_key_registry"]:
            context["foreign_key_registry"][f"{fk.tleft.__table_name__}.{fk.clause_name}"] = fk

        return None

    def get_all_foreign_key_accesses(self) -> ForeignKeyRegistryType:
        return self._get_context("foreign_key_registry").copy()

    def get_foreign_key_from_registry(self, key: str) -> Optional[ForeignKey]:
        """Get a specific ForeignKey from the registry by key"""
        return self._get_context("foreign_key_registry").get(key, None)

    def remove_foreign_key_from_registry(self, key: str) -> bool:
        """Remove a ForeignKey from the registry. Returns True if removed, False if not found"""
        context = self._get_context()
        if key in context["foreign_key_registry"]:
            del context["foreign_key_registry"][key]
            return True
        return False

    def clear_foreign_key_registry(self) -> None:
        """Clear only the ForeignKey registry while preserving other context"""
        context = self._get_context()
        context["foreign_key_registry"].clear()
        return None

    def get_foreign_key_registry_size(self) -> int:
        """Get the number of ForeignKeys in the registry"""
        return len(self._get_context("foreign_key_registry"))

    def clear_context(self):
        """Clear all context data (legacy method - use clear_all_context for clarity)"""
        self.clear_all_context()

    def clear_all_context(self) -> None:
        """Clear all context data including persistent ForeignKey registry"""
        if self.has_context():
            delattr(self._local, "context")

    def clear_transient_context(self) -> None:
        """Clear only transient context data, preserving ForeignKey registry"""
        if not self.has_context():
            return None

        context = self._get_context()
        # Preserve foreign_key_registry, clear everything else
        preserved_registry = context["foreign_key_registry"].copy()

        context["current_path"] = NO_CURRENT_PATH
        context["query_metadata"].clear()
        context["table_aliases"].clear()
        context["join_selector"].clear()
        # Restore preserved registry
        context["foreign_key_registry"] = preserved_registry

        return None

    def reset_query_context(self) -> None:
        """Reset context for new query while preserving persistent data"""
        self.clear_transient_context()

    def has_context(self) -> bool:
        return hasattr(self._local, "context")

    @contextmanager
    def query_context(self, table: Optional[Table] = None) -> Generator[PathContext, None, None]:
        """Context manager for query execution with proper cleanup"""
        # Store the old context if it exists
        old_context = None
        if self.has_context():
            old_context = self._get_context()

        try:
            self.initialize_context_with_table(table)
            yield self

        finally:
            # Restore old context or use selective clearing to preserve FK registry
            if old_context is not None:
                self._set_context(old_context)
            else:
                # Use selective clearing to preserve foreign_key_registry
                self.reset_query_context()

    def initialize_context_with_table(self, table: Optional[Table] = None) -> None:
        # Preserve foreign_key_registry if context already exists
        preserved_registry = {}
        if self.has_context():
            preserved_registry = self._get_context("foreign_key_registry").copy()

        self._set_context(self._initialize_context())

        # Restore preserved registry
        if preserved_registry:
            context = self._get_context()
            context["foreign_key_registry"] = preserved_registry

        if not table:
            return None

        initial_path = FKChain(table, [])
        self.set_current_path(initial_path)
        return None

    def reset_current_path(self, table):
        initial_path = FKChain(table, [])
        self.set_current_path(initial_path)
        return None

    #  FIXME [x]: Alias Management Methods (replacing ClauseInfoContext functionality)
    def add_table_alias(self, table: Table, alias: str) -> None:
        """Add a table alias to the context"""
        if not table or not alias:
            return None

        context = self._get_context()
        table_key = table.__table_name__ if hasattr(table, "__table_name__") else str(table)
        context["table_aliases"][table_key] = alias
        return None

    def get_table_alias(self, table: Table) -> Optional[str]:
        """Get a table alias from the context"""
        if not table:
            return None

        context = self._get_context()
        table_key = table.__table_name__ if hasattr(table, "__table_name__") else str(table)
        return context["table_aliases"].get(table_key, None)

    def add_join(self, join: JoinSelector, alias: str) -> None:
        """Add a table alias to the context"""
        if not join or not alias:
            return None

        context = self._get_context()
        context["join_selector"][alias] = join
        return None

    def get_join(self, alias: str) -> Optional[str]:
        """Get a table alias from the context"""
        if not alias:
            return None

        context = self._get_context("join_selector")
        return context.get(alias, None)


class FKChain:
    base: Optional[Table]
    steps: list[ForeignKey]

    def __init__(
        self,
        base: Optional[Table] = None,
        steps: Optional[list[Table]] = None,
    ):
        self.base = base if base else None
        self.steps = steps if steps else []

    def __repr__(self):
        return f"{FKChain.__name__}: {self.get_path_key()}"

    @property
    def parent(self) -> FKChain:
        # FIXME [ ]: what if we reach the top parent? we need to return None in some point
        if len(self.steps) <= 1:
            steps = []
        else:
            steps = self.steps[:-1].copy()

        return FKChain(self.base, steps)

    def add_step(self, step: Table | ForeignKey):
        """Add a step to the path"""
        if not self.base:
            self.base = step
            return None

        self.steps.append(step)
        return None

    def copy(self) -> FKChain:
        return FKChain(base=self.base, steps=self.steps.copy())

    def get_path_key(self) -> str:
        return self._generate_chain(".")

    def get_alias(self) -> str:
        """Generate table alias from the path"""
        if not self.base:
            return ""
        return self._generate_chain("_") if self.steps else self.base.__table_name__

    def _generate_chain(self, char: str) -> str:
        if not self.base:
            return ""
        result: list[Table] = [self.base.__table_name__]
        for step in self.steps:
            # For foreign keys, use their clause name or a descriptive name
            data = getattr(step, "clause_name", f"fk_{step.__class__.__name__}")
            result.append(data)
        return char.join(result)

    def get_depth(self) -> int:
        """Get the depth of this path (number of foreign key steps)"""
        return len(self.steps)

    def clear(self) -> None:
        self.steps.clear()

    def __getitem__(self, number: int):
        return FKChain(self.base, self.steps[number])


NO_CURRENT_PATH = FKChain(None, [])

PATH_CONTEXT = PathContext()
