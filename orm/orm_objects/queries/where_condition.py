from typing import Any, Callable, override

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
        *instances: tuple[*Inst],
        lambda_function: Callable[[*Inst], bool],
    ) -> None:
        self._instances: tuple[*Inst] = instances
        self._function: Callable[[*Inst], bool] = lambda_function

        self._tree: TreeInstruction = TreeInstruction(lambda_function)

    @override
    @property
    def query(self) -> str:
        return self._select_type_condition()


    def _select_type_condition(self)->Callable[[],Any]:
        n = len(self._tree.compare_op)
        dicc_selector:dict[int,Callable[[],str]] = {
            1:self.__comparable,
            2: self.__between_condition
        }
        return dicc_selector[n]()
        

    def __comparable(self)->str:
        c1,c2 = [x.nested_element.name for x in self._tree.to_list()]
        return f"{self.WHERE} {c1} {self._tree.compare_op[0]} {c2}"
    
    def __between_condition(self) -> str:
        query: str = self.WHERE
        c1,c2,c3 = [x.nested_element.name for x in self._tree.to_list()]
        for val in self._tree.to_list():
            nested_element = val.nested_element
            query += nested_element
        return query

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
