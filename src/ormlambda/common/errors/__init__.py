from __future__ import annotations
import inspect
import typing as tp

from ormlambda import util

if tp.TYPE_CHECKING:
    from ormlambda.sql.clause_info import ClauseInfo


class UnmatchedLambdaParameterError(Exception):
    def __init__(self, expected_params: int, function: tp.Callable[..., tp.Any], *args: object) -> None:
        super().__init__(*args)
        self.expected_params = expected_params
        self.found_param: tuple[str, ...] = tuple(inspect.signature(function).parameters)

    def __str__(self) -> str:
        return f"Unmatched number of parameters in lambda function with the number of tables: Expected {self.expected_params} parameters but found {str(self.found_param)}."


class NotKeysInIFunctionError(Exception):
    def __init__(self, match_regex: list[str], *args: object) -> None:
        super().__init__(*args)
        self._match_regex: list[str] = match_regex

    def __str__(self) -> str:
        return f"We cannot use placeholders in IFunction class. You used {self._match_regex}"


class FunctionFunctionError[T](Exception):
    def __init__(self, clause: ClauseInfo[T], *args):
        self.clause = clause
        super().__init__(*args)

    def __str__(self):
        agg_methods = self.__get_all_aggregate_method(self.clause)
        return f"You cannot use aggregation method like '{agg_methods}' to return model objects. Try specifying 'flavour' attribute as 'dict'."

    @util.preload_module("ormlambda.sql.functions")
    def __get_all_aggregate_method(self, clauses: list[ClauseInfo]) -> str:
        """
        Get the class name of those classes that inherit from 'IFunction' class in order to create a better error message.
        """

        IFunction = util.preloaded.sql_functions.IFunction 
        res: set[str] = set()
        if not isinstance(clauses, tp.Iterable):
            return clauses.__class__.__name__
        for clause in clauses:
            if isinstance(clause, IFunction):
                res.add(clause.__class__.__name__)
        return ", ".join(res)


class NotCallableError(ValueError):
    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self) -> str:
        return f"You must provide a function or callable to proceed with the query creation. Passed '{self.args[0].__class__.__name__}' "
