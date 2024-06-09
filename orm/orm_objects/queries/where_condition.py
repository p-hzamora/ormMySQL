from typing import Callable, override

from orm.dissambler.tree_instruction import TreeInstruction
from orm.interfaces.IQuery import IQuery


class WhereCondition[*Inst](IQuery):
    WHERE: str = "WHERE"
    __slots__ = [
        "_instances",
        "_function",
        "_tree",
    ]

    def __init__(
        self,
        instances: tuple[*Inst],
        lambda_function: Callable[[*Inst], bool],
    ) -> None:
        self._instances: tuple[*Inst] = instances
        self._function: Callable[[*Inst], bool] = lambda_function

        self._tree: TreeInstruction = TreeInstruction(lambda_function)

    @override
    @property
    def query(self) -> str:
        n = len(self._tree.compare_op)

        if n == 2:
            return self.__between_condition()
        else:
            query: str = self.WHERE
            for val in self._tree.to_list():
                nested_element = val.nested_element
                query += nested_element
            return query


    def __between_condition(self) -> str:
        return

    @classmethod
    def join_condition(cls, *args: "WhereCondition", restrictive=False) -> str:
        BY: str = "AND" if restrictive else "OR"
        query: str = f"{cls.WHERE}"

        n = len(args)
        for i in range(n):
            condition: WhereCondition = args[i]
            query += condition.query
            if i != n - 1:
                query += f" {BY}"

        return query
