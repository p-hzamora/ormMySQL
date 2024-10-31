from __future__ import annotations
import abc
import typing as tp


if tp.TYPE_CHECKING:
    from ormlambda import Table

    # TODOH: Changed to avoid mysql dependency
    from ormlambda.common.abstract_classes.decomposition_query import ClauseInfo

from .IQueryCommand import IQuery


class IDecompositionQuery[T: tp.Type[Table], *Ts](IQuery):
    @property
    @abc.abstractmethod
    def table(self) -> T: ...

    @property
    @abc.abstractmethod
    def tables(self) -> tuple[*Ts]: ...

    @property
    @abc.abstractmethod
    def lambda_query[*Ts](self) -> tp.Callable[[T], tuple[*Ts]]: ...

    @property
    @abc.abstractmethod
    def all_clauses(self) -> list[ClauseInfo]: ...

    @property
    @abc.abstractmethod
    def clauses_group_by_tables(self) -> dict[tp.Type[Table], list[ClauseInfo[T]]]: ...

    @property
    @abc.abstractmethod
    def fk_relationship(self) -> set[tuple[tp.Type[Table], tp.Type[Table]]]: ...

    @property
    @abc.abstractmethod
    def query(self) -> str: ...

    @property
    @abc.abstractmethod
    def alias(self) -> bool: ...

    @property
    @abc.abstractmethod
    def alias_name(self) -> tp.Optional[str]: ...

    @property
    @abc.abstractmethod
    def has_foreign_keys(self) -> bool: ...

    @abc.abstractmethod
    def stringify_foreign_key(self, sep: str = "\n"): ...

    @abc.abstractmethod
    def alias_children_resolver(self) -> tp.Callable[[tp.Type[Table], str], str]: ...
