from abc import ABC, abstractmethod
from typing import Any


class IUpdate(ABC):
    @abstractmethod
    def update(self, dicc: dict[str | property, Any]) -> None: ...
