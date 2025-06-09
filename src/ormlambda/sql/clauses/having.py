from __future__ import annotations

from .where import Where


class Having(Where):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    __visit_name__ = "having"

    def __init__(self, *comparer, restrictive=True, context=None, **kw):
        super().__init__(*comparer, restrictive=restrictive, context=context, **kw)

    @staticmethod
    def FUNCTION_NAME() -> str:
        return "HAVING"


__all__ = ["Having"]
