import sys
import os
from pathlib import Path
import unittest
from datetime import datetime
import dotenv


dotenv.load_dotenv()

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from test.models.address import Address, AddressModel  # noqa: E402
from orm import MySQLRepository  # noqa: E402
from orm.databases.my_sql.clauses import SelectQuery  # noqa: E402


repo = MySQLRepository("")
class TestFK(unittest.TestCase):
    def test_fk(self):
        a = Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid", datetime.now())
        
         

        sakila_db = MySQLRepository(USERNAME,PASSWORD,"sakila")

        a_model = AddressModel(sakila_db)
        country = a_model.get(a.city.country.country)
        self.assertEqual(country, "España")

        SelectQuery[Address](Address, lambda x: (x.address, x.city))


if __name__ == "__main__":

    unittest.main()
