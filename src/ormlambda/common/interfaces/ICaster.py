
from __future__ import annotations
from typing import TYPE_CHECKING
import abc

if TYPE_CHECKING:
    from ormlambda.common.abstract_classes.caster.cast_base import WriteCastBase, ReadCastBase


class ICaster(abc.ABC):
    WRITE: WriteCastBase = ...
    READ: ReadCastBase = ...
