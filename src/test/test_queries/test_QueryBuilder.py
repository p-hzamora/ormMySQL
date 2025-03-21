import unittest
import sys
from pathlib import Path

sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())

from models import Address
from ormlambda.databases.my_sql.statements import QueryBuilder
from ormlambda.databases.my_sql.clauses import (
    Limit,
    Offset,
    Order,
    Select,
    UpsertQuery,
    UpdateQuery,
    Where,
    Count,
    GroupBy,
    Alias,
)


class TestQueryBuilder(unittest.TestCase): ...

if __name__ == "__main__":
    unittest.main()
