import unittest
import sys
from pathlib import Path


sys.path = [str(Path(__file__).parent.parent), *sys.path]
sys.path.append([str(x) for x in Path(__file__).parents if x.name == "src"].pop())

from ormlambda.databases.my_sql.clauses.select import Select  # noqa: E402
from models import Address  # noqa: E402

ADDRESS_1 = Address(200, "Calle Cristo de la victoria", None, None, 1, "28026", "617128992", "Usera", None)


class TestCondition(unittest.TestCase):
    def test_cols_from_foreign_keys(self):
        # this response must not be the real one,
        q = Select[Address](
            Address,
            columns=(
                Address.City.city_id,
                Address.address,
                Address.City.city_id,
                Address.City.Country,
            ),
        )
        self.assertEqual(
            q.query,
            "SELECT address.address_id as `address_address_id`, address.address as `address_address`, address.address2 as `address_address2`, address.district as `address_district`, address.city_id as `address_city_id`, address.postal_code as `address_postal_code`, address.phone as `address_phone`, address.location as `address_location`, address.last_update as `address_last_update`, city.city_id as `city_city_id`, city.city as `city_city`, city.country_id as `city_country_id`, city.last_update as `city_last_update`, country.country_id as `country_country_id`, country.country as `country_country`, country.last_update as `country_last_update`, city.country_id as `city_country_id`, address.city_id as `address_city_id`, address.last_update as `address_last_update`, country.country as `country_country` FROM address INNER JOIN city ON address.city_id = city.city_id INNER JOIN country ON city.country_id = country.country_id",
        )


if __name__ == "__main__":
    unittest.main()
