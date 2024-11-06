from __future__ import annotations
import abc


from .IQueryCommand import IQuery
class IJoinSelector[TLeft, TRight](IQuery):

    @abc.abstractmethod
    def sort_join_selectors(cls, joins: set[IJoinSelector]) -> tuple[IJoinSelector]: ...