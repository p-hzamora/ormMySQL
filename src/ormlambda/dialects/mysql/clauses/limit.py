from ormlambda.sql.clauses import Limit


class Limit(Limit):
    def __init__(self, number):
        super().__init__(number)
