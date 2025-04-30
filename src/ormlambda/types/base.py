import enum


class DatabaseType(str, enum.Enum):
    MYSQL = "mysql"
    SQLITE = "sqlite"
    POSTGRESQL = "postgressql"

    def __str__(self):
        return super().__str__()
