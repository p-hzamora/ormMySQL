from .column import Column


class ForeignKey[T]():
    def __init__(
        self,
        referenced_column:str,
    ) -> None:
        self._referenced_column = referenced_column
        pass
