from __future__ import annotations
import typing as tp
import abc

from .IQueryCommand import IQuery


class IAggregate[T](IQuery):
    @classmethod
    @abc.abstractmethod
    def FUNCTION_NAME(cls) -> str: ...

    @property
    @abc.abstractmethod
    def alias_clause(self) -> tp.Optional[str]: ...
