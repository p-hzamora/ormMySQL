import unittest
import sys
from pathlib import Path


sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda.sql.clause_info.clause_info_context import ClauseInfoContext
from ormlambda.common.abstract_classes.decomposition_query import DecompositionQueryBase
from models import Address
from ormlambda import ORM

from ormlambda.databases.my_sql import MySQLRepository
from config import config_dict

ddbb = MySQLRepository(**config_dict)


class TestQueryBuilder(unittest.TestCase): ...


if __name__ == "__main__":
    unittest.main()
