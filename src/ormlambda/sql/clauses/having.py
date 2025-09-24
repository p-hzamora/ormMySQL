from __future__ import annotations

from .where import Where


class Having(Where):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    __visit_name__ = "having"

    def __init__(self, *comparer, restrictive=True, **kw):
        super().__init__(*comparer, restrictive=restrictive, **kw)



__all__ = ["Having"]
