import sys
from pathlib import Path
import unittest
from datetime import datetime


sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm.orm_objects.foreign_key import ForeignKey  # noqa: E402
from test.models import Address,City,Country  # noqa: E402
from orm.orm_objects.queries import SelectQuery  # noqa: E402


class TestFK(unittest.TestCase):
    def test_fk(self):
        a = Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid", datetime.now())


        mapped = ForeignKey.MAPPED
        self.assertEqual(mapped[Address.__table_name__]["city_id"].col,"city_id")


        SelectQuery[Address](Address, lambda x: (x.address, x.city))


if __name__ == "__main__":
    unittest.main()
