import enum


class UnionEnum(str, enum.Enum):
    AND = "AND"
    OR = "OR"

    def __str__(self):
        return super().__str__()