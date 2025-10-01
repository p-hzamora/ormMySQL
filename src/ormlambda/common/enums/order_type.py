import enum


class OrderType(str, enum.Enum):
    def __str__(self):
        return super().__str__()

    ASC = "ASC"
    DESC = "DESC"
