from __future__ import annotations
import threading
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator, Literal, Optional, Any, TypedDict, Protocol


if TYPE_CHECKING:
    from ormlambda import Table
    from ormlambda.sql import ForeignKey
    from ormlambda.sql.context import FKChain


type CurrentPathType = FKChain
type ForeignKeyRegistryType = dict[str, ForeignKey]
type QueryMetadataType = dict[str, Any]

type ContextDictKeys = Literal["current_path", "foreign_key_registry", "query_metadata"]


class ContextDict(TypedDict):
    current_path: CurrentPathType
    foreign_key_registry: ForeignKeyRegistryType
    query_metadata: QueryMetadataType


class LocalContext(Protocol):
    context: ContextDict


class PathContext:
    _local: LocalContext

    def __init__(self):
        self._local = threading.local()

    @staticmethod
    def _initialize_context() -> ContextDict:
        return {
            "current_path": NO_CURRENT_PATH,
            "foreign_key_registry": {},
            "query_metadata": {},
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
            context["foreign_key_registry"][f"{fk.tleft}.{fk.tright}"] = fk

        return None

    def get_all_foreign_key_accesses(self) -> ForeignKeyRegistryType:
        return self._get_context("foreign_key_registry").copy()


    def clear_context(self):
        """Clear the current path"""
        if self.has_context():
            delattr(self._local, "context")

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
            # Restore old context or clear if none existed
            if old_context is not None:
                self._set_context(old_context)
            else:
                self.clear_context()

    def initialize_context_with_table(self, table: Optional[Table] = None) -> None:
        self._set_context(self._initialize_context())

        if not table:
            return None

        initial_path = FKChain(table, [])
        self.set_current_path(initial_path)
        return None

    def reset_current_path(self, table):
        initial_path = FKChain(table, [])
        self.set_current_path(initial_path)
        return None


class FKChain:
    base: Optional[Table]
    steps: list[Table | ForeignKey]

    def __init__(
        self,
        base: Optional[Table] = None,
        steps: Optional[list[Table]] = None,
    ):
        self.base = base if base else None
        self.steps = steps if steps else []

    def __repr__(self):
        return f"{FKChain.__name__}: {self.get_path_key()}"

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
        return self._generate_chain("_") if self.steps else self.base.__table_name__

    def _generate_chain(self, char: str) -> str:
        result: list[Table] = [self.base.__table_name__]
        for step in self.steps:
            # For foreign keys, use their clause name or a descriptive name
            data = getattr(step, "clause_name", f"fk_{step.__class__.__name__}")
            result.append(data)
        return char.join(result)

    def get_depth(self) -> int:
        """Get the depth of this path (number of foreign key steps)"""
        return len([step for step in self.steps if hasattr(step, "clause_name")])

    def get_foreign_keys(self) -> list[ForeignKey]:
        """Get all foreign keys in this path"""
        from ormlambda import ForeignKey

        return [step for step in self.steps if isinstance(step, ForeignKey)]


NO_CURRENT_PATH = FKChain(None, [])

PATH_CONTEXT = PathContext()
