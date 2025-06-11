from __future__ import annotations

from ormlambda.sql.clauses import Order


class Order(Order):
    def __init__(self, column, order_type, context=None):
        super().__init__(column, order_type, context)
