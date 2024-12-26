import inspect
import typing as tp


class UnmatchedLambdaParameterError(Exception):
    def __init__(self, expected_params: int, function: tp.Callable[..., tp.Any], *args: object) -> None:
        super().__init__(*args)
        self.expected_params = expected_params
        self.found_param: tuple[str, ...] = tuple(inspect.signature(function).parameters)

    def __str__(self) -> str:
        return f"Unmatched number of parameters in lambda function with the number of tables: Expected {self.expected_params} parameters but found {str(self.found_param)}."


class NotKeysInIAggregateError(Exception):
    def __init__(self, match_regex: list[str], *args: object) -> None:
        super().__init__(*args)
        self._match_regex: list[str] = match_regex

    def __str__(self) -> str:
        return f"We cannot use placeholders in IAggregate class. You used {self._match_regex}"
