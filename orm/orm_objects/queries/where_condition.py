from collections import defaultdict
from queue import Queue
from typing import Callable, overload, Optional

from orm.dissambler import Dissambler



class WhereCondition[TProp1, TProp2](Dissambler[TProp1, TProp2]):
    WHERE: str = "WHERE"
    __slots__ = [
        "_instance_tbl_1",
        "_instance_tbl_2",
        "_function",
    ] + list(Dissambler.__slots__)


    def __init__(
        self,
        instance_tbl_1:TProp1,
        instance_tbl_2:TProp2,
        lambda_function: Callable[[TProp1], bool] | Callable[[TProp1, TProp2], bool],
    ) -> None:
        
        self._instance_tbl_1:TProp1 = instance_tbl_1
        self._instance_tbl_2:TProp2 = instance_tbl_2
        self._function: Callable[[TProp1, TProp2], bool] = lambda_function


        super().__init__(lambda_function)

    def to_query(self) -> str:
        try:
            cond_2_name = getattr(self._instance_tbl_2,self.cond_2.name)
        except Exception:
            cond_2_name = self.cond_2.name
        return f"{self.WHERE} {self.cond_1.name} {self.compare_op} {cond_2_name}"

    @classmethod
    def join_condition(cls, *args: "WhereCondition", restrictive=False) -> str:
        BY: str = "AND" if restrictive else "OR"
        query:str = f"{cls.WHERE}"

        n = len(args)
        for i in range(n):
            condition:WhereCondition = args[i]
            query += f" ({condition.cond_1.name} {condition.compare_op} {condition.cond_2.name})"
            if i != n - 1:
                query += f" {BY}"

        return query
