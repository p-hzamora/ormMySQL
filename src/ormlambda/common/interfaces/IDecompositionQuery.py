from __future__ import annotations
import abc
import typing as tp


if tp.TYPE_CHECKING:
    from ormlambda.utils.foreign_key import ForeignKey
    from ormlambda.utils.table_constructor import Table

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
    def lambda_query[*Ts](self) -> tp.Callable[[T], tuple[*Ts]]: ...

    @property
    @abc.abstractmethod
    def all_clauses(self) -> list[ClauseInfo]: ...

    @property
    @abc.abstractmethod
    def fk_relationship(self) -> set[tuple[TableType, TableType]]: ...

    @property
    @abc.abstractmethod
    def has_foreign_keys(self) -> bool: ...

    @abc.abstractmethod
    def stringify_foreign_key(self, sep: str = "\n"): ...

    @abc.abstractmethod
    def _add_fk_relationship[RTable: tp.Type[Table]](self, foreign_key: ForeignKey[T, RTable]) -> None: ...
