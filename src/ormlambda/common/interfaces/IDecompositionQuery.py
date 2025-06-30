from __future__ import annotations
import abc
import typing as tp


if tp.TYPE_CHECKING:
    # TODOH: Changed to avoid mysql dependency
    from ormlambda.sql.clause_info import ClauseInfo, TableType


class IDecompositionQuery_one_arg[T: TableType]:
    @property
    @abc.abstractmethod
    def table(self) -> T: ...



class IDecompositionQuery[T: TableType, *Ts](IDecompositionQuery_one_arg[T]):
    @property
    @abc.abstractmethod
    def tables(self) -> tuple[*Ts]: ...

    @property
    @abc.abstractmethod
    def all_clauses(self) -> list[ClauseInfo]: ...
