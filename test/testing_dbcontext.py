import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path = [str(Path(__file__).parent.parent), *sys.path]

from orm import MySQLRepository, IRepositoryBase  # noqa: E402
from orm.condition_types import ConditionType  # noqa: E402
from test.models.address import AddressModel, Address  # noqa: E402


load_dotenv()


USERNAME = "root"  # os.getenv("DB_USERNAME")
PASSWORD = "1234"  # os.getenv("DB_PASSWORD")
HOST = "localhost"  # os.getenv("DB_HOST")


database: IRepositoryBase = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST).connect()


a_model = AddressModel(database)
address = (
    a_model.where(lambda a: 177 >= a.address_id >= 28)
    .where(lambda x: (x.city.country.country, ConditionType.REGEXP, r"^[FHA]"))
    .where(lambda x: (x.city.city, ConditionType.REGEXP, r"[^W]"))
    .order(lambda a: a.address_id, order_type="DESC")
    .select(
        lambda a: (
            a.address_id,
            a.city.country.country,
            a.city.city,
            a.address,
        ),
        flavour=tuple,
    )
)

query = """
SELECT address.address_id as `kkk`, country.country as `country_country`, city.city as `city_city`, address.address as `address_address` FROM address INNER JOIN city ON address.city_id = city.city_id INNER JOIN country ON city.country_id = country.country_id
WHERE country.country REGEXP '^[FHA]' AND (city.city REGEXP '[^W]') AND (177 >= address.address_id) AND (address.address_id <= 28)
ORDER BY address.address_id DESC
"""
address = a_model._repository.read_sql(query, flavour=dict)
pass


address = a_model.where(lambda x: x.address_id == 1).select()

print(address.phone)
address.phone = 10000000
a_model.upsert(address)

address = a_model.where(lambda x: x.address_id == 1).select()
print(address.phone)
