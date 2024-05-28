import sys
from pathlib import Path
import unittest
from datetime import datetime


sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from test.models import Address, Country, City  # noqa: E402
from orm.orm_objects.foreign_key import ForeignKey  # noqa: E402
from orm.orm_objects.queries import SelectQuery


class TestFK(unittest.TestCase):
    def test_fk(self):
        a = Address(1, "panizo", None, "tetuan", 28900, 26039, "617128992", "Madrid", datetime.now())

        aa = Address()

        
        self.assertTrue(a.address_id,1)
        self.assertTrue(a.address,"panizo")
        self.assertTrue(a.address2,None)
        self.assertTrue(a.district,"tetuan")
        self.assertTrue(a.city_id,28900)
        self.assertTrue(a.postal_code,26039)
        self.assertTrue(a.phone,"617128992")
        self.assertTrue(a.location,"Madrid")
        self.assertTrue(a.last_update,datetime.now())
        
        SelectQuery[Address](Address,lambda x: (x.address,x.city))

if __name__ == "__main__":
    unittest.main()
