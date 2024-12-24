from __future__ import annotations
import abc


from .IQueryCommand import IQuery


class IJoinSelector[TLeft, TRight](IQuery):
    @abc.abstractmethod
    def sort_join_selectors(cls, joins: set[IJoinSelector]) -> tuple[IJoinSelector]: ...

    @property
    def left_table(self) -> str: ...
    @property
    def right_table(self) -> str: ...
    @property
    def left_col(self) -> str: ...
    @property
    def right_col(self) -> str: ...
    @property
    def alias(self) -> str: ...
