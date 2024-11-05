class UnmatchedLambdaParameterError(Exception):
    def __init__(self, expected_params: int, found_param: tuple[str, ...], *args: object) -> None:
        super().__init__(*args)
        self.expected_params = expected_params
        self.found_param: tuple[str, ...] = found_param

    def __str__(self) -> str:
        return f"Unmatched number of parameters in lambda function with the number of tables: Expected {self.expected_params} parameters but found {str(self.found_param)}."
