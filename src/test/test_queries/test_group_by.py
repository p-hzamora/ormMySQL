import sys
from pathlib import Path
import unittest

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda import ORM, Count
from test.config import create_sakila_engine
from test.models import Address


engine = create_sakila_engine()


class TestGroupBy(unittest.TestCase):
    def test_groupby(self) -> None:
        model = ORM(Address, engine)

        # fmt: off
        (
            model
                .groupby(lambda x: x.address)
                .select(lambda x: (
                    x.address,
                    Count(x.City.Country.country_id,'contar')
                ),flavour=dict,
            )
        )
        # fmt: on


if __name__ == "__main__":
    unittest.main()
