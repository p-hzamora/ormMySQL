from abc import ABC
import json
# from .foreign_key import ForeignKey


class Table(ABC):
    __table_name__: str = ...

    # foreign_key: ForeignKey = ForeignKey

    def __repr__(self) -> str:
        params = ", ".join([f"{x}={getattr(self,x)}" for x, y in self.__class__.__dict__.items() if isinstance(y, property)])
        return f"{self.__class__.__name__}({params})"

    def __str__(self) -> str:
        params = {x: getattr(self, x) for x, y in self.__class__.__dict__.items() if isinstance(y, property)}
        return json.dumps(params, ensure_ascii=False, indent=2)
