from ormlambda.sql.clauses import Offset


class Offset(Offset):
    def __init__(self, number):
        super().__init__(number)
