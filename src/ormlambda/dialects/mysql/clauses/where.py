from __future__ import annotations
from ormlambda.sql.clauses import Where


class Where(Where):
    def __init__(self, *comparer, restrictive=True, context=None):
        super().__init__(*comparer, restrictive=restrictive, context=context)
