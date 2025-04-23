from __future__ import annotations
from ormlambda.sql.clauses import _Where


class Where(_Where):
    def __init__(self, *comparer, restrictive=True, context=None):
        super().__init__(*comparer, restrictive=restrictive, context=context)
