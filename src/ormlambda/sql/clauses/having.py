from __future__ import annotations

from .where import _Where


class _Having(_Where):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    def __init__(self, *comparer, restrictive=True, context=None):
        super().__init__(*comparer, restrictive=restrictive, context=context)

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "HAVING"


__all__ = ["_Having"]
