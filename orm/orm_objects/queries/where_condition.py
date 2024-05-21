from collections import defaultdict
from queue import Queue
from typing import Callable, overload, Optional

from orm.dissambler import Dissambler


class WhereCondition[TProp1, TProp2](Dissambler[TProp1, TProp2]):
    WHERE: str = "WHERE"
    __slots__ = [
        "_function",
        "_conditions",
        "_table_cond_1",
        "_table_cond_2",
    ] + list(Dissambler.__slots__)

    @overload
    def __init__(self, lambda_function: Callable[[TProp1], bool]) -> None: ...

    @overload
    def __init__(self, lambda_function: Callable[[TProp1], bool], table_cond_1: Optional[str]) -> None: ...

    @overload
    def __init__(self, lambda_function: Callable[[TProp1, TProp2], bool]) -> None: ...

    @overload
    def __init__(self, lambda_function: Callable[[TProp1, TProp2], bool], table_cond_2: Optional[str]) -> None: ...

    def __init__(
        self,
        lambda_function: Callable[[TProp1], bool] | Callable[[TProp1, TProp2], bool],
        table_cond_1: Optional[str] = None,
        table_cond_2: Optional[str] = None,
    ) -> None:
        self._function: Callable[[TProp1, TProp2], bool] = lambda_function
        self._table_cond_1: str = table_cond_1
        self._table_cond_2: str = table_cond_2
        self._conditions: dict[str, Queue] = defaultdict(Queue)

        super().__init__(lambda_function)

    @property
    def table_cond_1(self) -> str:
        return self._table_cond_1 if self._table_cond_1 else ""

    @property
    def table_cond_2(self) -> str:
        return self._table_cond_2 if self._table_cond_2 else ""

    def to_query(self) -> str:
        return f"{self.WHERE} {self.cond_1.name} {self.compare_op} {self.cond_2.name}"

    @classmethod
    def join_condition(cls, *args: "WhereCondition", restrictive=False) -> "WhereCondition":
        BY: str = "AND" if restrictive else "OR"
        query = f"{cls.WHERE}"

        n = len(args)
        for i in range(n):
            condition = args[i]
            query += f" ({condition.cond_1.name} {condition.compare_op} {condition.cond_2.name})"
            if i != n - 1:
                query += f" {BY}"

        return query
