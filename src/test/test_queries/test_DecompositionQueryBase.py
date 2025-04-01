import unittest

from ormlambda.databases.my_sql import MySQLRepository

from test.config import config_dict

ddbb = MySQLRepository(**config_dict)


class TestQueryBuilder(unittest.TestCase): ...


if __name__ == "__main__":
    unittest.main()
