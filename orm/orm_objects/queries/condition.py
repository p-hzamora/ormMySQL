from collections import defaultdict
from queue import Queue
from typing import Callable, overload, Optional

from orm.dissambler import Dissambler


class Condition[TProp1, TProp2](Dissambler[TProp1, TProp2]):
    WHERE: str = "WHERE"
    __slots__ = (
        "_function",
        "_conditions",
        "_table_cond_1",
        "_table_cond_2",
        "_cond_1",
        "_cond_2",
        "_compare_op",
    )

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
    def cond_1(self) -> str:
        return self._cond_1

    @property
    def cond_2(self) -> str:
        return self._cond_2

    @property
    def table_cond_1(self) -> str:
        return self._table_cond_1 if self._table_cond_1 else ""

    @property
    def table_cond_2(self) -> str:
        return self._table_cond_2 if self._table_cond_2 else ""

    @property
    def compare_symbol(self) -> str:
        return self._compare_op

    def to_query(self) -> str:
        return f"{self.WHERE} {self.cond_1} {self.compare_symbol} {self.cond_2}"

    @classmethod
    def join_condition(cls, *args: "Condition", restrictive=False) -> "Condition":
        BY: str = "AND" if restrictive else "OR"
        query = f"{cls.WHERE}"

        n = len(args)
        for index in range(n):
            condition = args[index]
            query += f" ({condition.cond_1} {condition.compare_symbol} {condition.cond_2})"
            if index != n - 1:
                query += f" {BY}"

        return query
