from ormlambda.statements.base_statement import BaseStatement


class SQLiteStatements[T,*Ts](BaseStatement[T]):
    def __init__(self, model, repository):
        super().__init__(model, repository)
        self._wuer