from __future__ import annotations
import abc
import typing as tp


if tp.TYPE_CHECKING:
    from ormlambda.databases.my_sql.clauses.joins import JoinSelector

    # TODOH: Changed to avoid mysql dependency
    from ormlambda.common.abstract_classes.clause_info import ClauseInfo, TableType

from .IQueryCommand import IQuery


class IDecompositionQuery_one_arg[T: TableType](IQuery):
    @property
    @abc.abstractmethod
    def table(self) -> T: ...


class IDecompositionQuery[T: TableType, *Ts](IDecompositionQuery_one_arg[T], IQuery):
    @property
    @abc.abstractmethod
    def tables(self) -> tuple[*Ts]: ...

    @property
    @abc.abstractmethod
    def all_clauses(self) -> list[ClauseInfo]: ...

    @abc.abstractmethod
    def stringify_foreign_key(self, joins: set[JoinSelector], sep: str = "\n"): ...
