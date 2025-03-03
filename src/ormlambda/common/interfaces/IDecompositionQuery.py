from __future__ import annotations
import abc
import typing as tp


if tp.TYPE_CHECKING:
    # TODOH: Changed to avoid mysql dependency
    from ormlambda.sql.clause_info import ClauseInfo, TableType
    from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext


class IDecompositionQuery_one_arg[T: TableType]:
    @property
    @abc.abstractmethod
    def table(self) -> T: ...

    @property
    @abc.abstractmethod
    def context(self) -> tp.Optional[ClauseInfoContext]: ...

    @context.setter
    @abc.abstractmethod
    def context(self) -> tp.Optional[ClauseInfoContext]: ...


class IDecompositionQuery[T: TableType, *Ts](IDecompositionQuery_one_arg[T]):
    @property
    @abc.abstractmethod
    def tables(self) -> tuple[*Ts]: ...

    @property
    @abc.abstractmethod
    def all_clauses(self) -> list[ClauseInfo]: ...
