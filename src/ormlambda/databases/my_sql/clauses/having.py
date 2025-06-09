from __future__ import annotations

from ormlambda.sql.clauses import Having


class Having(Having):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    def __init__(self, *comparer, restrictive=True, context=None):
        super().__init__(*comparer, restrictive=restrictive, context=context)
