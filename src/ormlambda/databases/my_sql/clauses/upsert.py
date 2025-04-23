from __future__ import annotations

from ormlambda import Table
from ormlambda.sql.clauses.upsert import _Upsert


class UpsertQuery[T: Table](_Upsert):
    def __init__(self, model, repository):
        super().__init__(model, repository)
