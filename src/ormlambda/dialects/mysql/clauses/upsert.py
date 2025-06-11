from __future__ import annotations

from ormlambda import Table
from ormlambda.sql.clauses.upsert import Upsert


class UpsertQuery[T: Table](Upsert):
    def __init__(self, model, repository):
        super().__init__(model, repository)
