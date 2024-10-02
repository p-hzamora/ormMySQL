from typing import Type


class Column[T]:
    __slots__ = (
        "dtype",
        "column_name",
        "column_value",
        "is_primary_key",
        "is_auto_generated",
        "is_auto_increment",
        "is_unique",
    )

    def __init__(
        self,
        dtype: Type[T] = None,
        column_name: str = None,
        column_value: T = None,
        *,
        is_primary_key: bool = False,
        is_auto_generated: bool = False,
        is_auto_increment: bool = False,
        is_unique: bool = False,
    ) -> None:
        self.dtype = dtype
        self.column_name = column_name
        self.column_value: T = column_value
        self.is_primary_key: bool = is_primary_key
        self.is_auto_generated: bool = is_auto_generated
        self.is_auto_increment: bool = is_auto_increment
        self.is_unique: bool = is_unique

    def __repr__(self) -> str:
        return f"<Column: {self.column_name}>"

    def __to_string__(self, name: str, var_name: T, type_: str):
        dicc: dict = {
            "dtype": type_,
            "column_name": f"'{name}'",
            "column_value": var_name,  # must be the same variable name as the instance variable name in Table's __init__ class
        }
        exec_str: str = f"{Column.__name__}[{type_}]("
        for x in self.__slots__:
            self_value = getattr(self, x)

            exec_str += f"  {x}={dicc.get(x,self_value)},\n"
        exec_str += ")"
        return exec_str

    def __hash__(self) -> int:
        return hash(
            (
                self.column_name,
                self.column_value,
                self.is_primary_key,
                self.is_auto_generated,
                self.is_auto_increment,
                self.is_unique,
            )
        )

    def __eq__(self, value: "Column") -> bool:
        if isinstance(value, Column):
            return self.__hash__() == value.__hash__()
        return False
