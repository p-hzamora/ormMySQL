from __future__ import annotations
from typing import TYPE_CHECKING


from ormlambda.sql.clauses import JoinSelector

# TODOL [x]: Try to import Table module without circular import Error
if TYPE_CHECKING:
    from ormlambda import Table


class JoinSelector[TLeft: Table, TRight: Table](JoinSelector[TLeft, TRight]):
    def __init__(self, where, by, alias="{table}", context=None, **kw):
        super().__init__(where, by, alias, context, **kw)
