from ormlambda.sql.clauses import _Offset


class Offset(_Offset):
    def __init__(self, number):
        super().__init__(number)
