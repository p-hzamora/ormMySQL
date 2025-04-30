from ormlambda.sql.clauses import _Limit


class Limit(_Limit):
    def __init__(self, number):
        super().__init__(number)
