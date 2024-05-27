class Column[T]:
    __slots__ = (
        "column_name",
        "column_value",
        "is_primary_key",
        "is_auto_generated",
        "is_auto_increment",
        "is_unique",
    )

    def __init__(
        self,
        column_name,
        column_value,
        *,
        is_primary_key: bool = False,
        is_auto_generated: bool = False,
        is_auto_increment: bool = False,
        is_unique: bool = False,
    ) -> None:
        self.column_name: str = column_name
        self.column_value: T = column_value
        self.is_primary_key: bool = is_primary_key
        self.is_auto_generated: bool = is_auto_generated
        self.is_auto_increment: bool = is_auto_increment
        self.is_unique: bool = is_unique

    def __repr__(self) -> str:
        return f"<Column: {self.column_name}>"
