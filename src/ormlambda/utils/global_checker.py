from typing import Any


class GlobalChecker:
    @staticmethod
    def is_lambda_function(obj: Any) -> bool:
        return callable(obj) and not isinstance(obj, type)
