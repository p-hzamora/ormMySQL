from __future__ import annotations
import typing as tp

if tp.TYPE_CHECKING:
    from ormlambda import Table
from .IQueryCommand import IQuery
from .IDecompositionQuery import IDecompositionQuery


class IAggregate[T: tp.Type[Table]](IDecompositionQuery[T], IQuery): ...
