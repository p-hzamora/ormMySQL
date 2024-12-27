from __future__ import annotations
import abc

from .IQueryCommand import IQuery


class IAggregate(IQuery):
    @classmethod
    @abc.abstractmethod
    def FUNCTION_NAME(cls) -> str: ...
