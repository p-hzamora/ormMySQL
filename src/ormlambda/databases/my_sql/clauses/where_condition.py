from __future__ import annotations
import typing as tp
from ormlambda.common.abstract_classes.comparer import Comparer
from ormlambda.common.interfaces import IAggregate

if tp.TYPE_CHECKING:
    from ormlambda.common.abstract_classes.clause_info import ClauseInfo


class WhereCondition(IAggregate):
    FUNCTION_NAME: str = "WHERE"
    """
    The purpose of this class is to create 'WHERE' condition queries properly.

    Args.
        - instances: tuple[*Inst],
            - passed all instance that we are going to use inside of `function` arg

        - function: Callable[[*Inst], bool] = lambda: None,
            - lambda function to create condition between instance variables
        - **kwargs: Any,
            - We use this clause by passing all the variables that we want to replace inside the lambda function.
            When we try to disassemble the lambda function, we see that the variables were not replaced by their values.
            Instead, we only got the variable names, not the values.
            Due to this problem, we need to specify the correct dictionary to map variable names to their values.

    >>> var = 100
    >>> _lambda = lambda a: a.city_id <= var
    >>> ... #Dissamble _lambda method
    >>> parts_of_lambda = [
    >>>     "city_id"
    >>>     "<="
    >>>     "var"                   <-------- We excepted 100
    >>> ]
    """

    def __init__(self, compare: Comparer) -> None:
        self._compare: Comparer = compare

    # FIXME [ ]: that's an error. We need to keep in mind that left_condition could be Compare
    @property
    def left_condition(self) -> ClauseInfo:
        return self._compare.left_condition

    @property
    def right_condition(self) -> ClauseInfo:
        return self._compare.right_condition

    @property
    def query(self) -> str:
        return f"{self.FUNCTION_NAME} {self._compare.query}"

    @property
    def alias_clause(self) -> None:
        return None
