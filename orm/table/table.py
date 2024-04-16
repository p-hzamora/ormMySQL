from abc import ABC
from typing import Optional
import json


class Table(ABC):
    __table_name__: str = ...

    def __repr__(self) -> str:
        params = ", ".join(
            [
                f"{x}={getattr(self,x)}"
                for x, y in self.__class__.__dict__.items()
                if isinstance(y, property)
            ]
        )
        return f"{self.__class__.__name__}({params})"

    def __str__(self) -> str:
        params = {
            x: getattr(self, x)
            for x, y in self.__class__.__dict__.items()
            if isinstance(y, property)
        }
        return json.dumps(params, ensure_ascii=False, indent=2)

    @staticmethod
    def __swap_dicc_values[TKey, TValue](
        dicc: dict[TKey, TValue], key: TKey, default_key: TKey = None
    ) -> Optional[TValue]:
        if key is None:
            return None

        if default_key is None:
            default_key = dicc.keys()[-1]

        integer = dicc.get(key, dicc[default_key])
        return integer

    @classmethod
    def swap_string_to_int(cls, string: str) -> Optional[int]:
        selection: dict[str, int] = {"si": 1, "no": 0}
        return cls.__swap_dicc_values(selection, string, "no")

    @classmethod
    def swap_int_to_bool(cls, integer: int) -> Optional[bool]:
        selection: dict[int, bool] = {1: True, 0: False}
        return cls.__swap_dicc_values(selection, integer, 0)

    @classmethod
    def swap_bool_to_int(cls, integer: int) -> Optional[bool]:
        selection: dict[bool, int] = {True: 1, False: 0}
        return cls.__swap_dicc_values(selection, integer, 0)
