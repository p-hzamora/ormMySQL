import datetime
import sys
from pathlib import Path


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda import create_engine, Table, Column, ORM
from ormlambda.dialects.mysql.types import (
    SMALLINT,
    VARCHAR,
    TEXT,
    DATETIME,
)

from test.models import Address, Country, City


class Users(Table):
    __table_name__ = "users"
    id: SMALLINT = Column(SMALLINT(unsigned=True, zerofill=True), is_primary_key=True)
    username: VARCHAR = Column(VARCHAR(50), is_not_null=False, is_unique=True)
    email: VARCHAR = Column(VARCHAR(100), is_not_null=False)
    password_hash: VARCHAR = Column(VARCHAR(128), is_not_null=False)
    bio: TEXT = Column(TEXT(), is_not_null=True)
    created_at: DATETIME = Column(DATETIME(), default=datetime.datetime.utcnow)


# mysql = create_engine("mysql+mysqlconnector://root:1500@localhost:3306/sakila")
# sqlite = create_engine("sqlite:///~/Downloads/sakila.db")

# url_connection = "mysql://root:1500@localhost:3306?pool_size=3"

# engine = create_engine(url_connection)
# TEST_DB = "casa"

# engine.repository._pool
# if engine.schema_exists(TEST_DB):
#     engine.drop_schema(TEST_DB, True)
# engine.create_schema(TEST_DB, True)

new_url = "mysql://root:1500@localhost:3306?pool_size=3"
sakila_url = "mysql://root:1500@localhost:3306/sakila?pool_size=3"
new_engine = create_engine(new_url)
sakila_engine = create_engine(sakila_url)

TEST = "TEST"

if new_engine.schema_exists(TEST):
    new_engine.drop_schema(TEST)
new_engine.create_schema(TEST, False)
new_engine.set_database(TEST)
ORM(Country, new_engine).create_table("replace")
ORM(City, new_engine).create_table("replace")
ORM(Address, new_engine).create_table("replace")


sakila_country = ORM(Country, sakila_engine)
sakila_city = ORM(City, sakila_engine)
sakila_address = ORM(Address, sakila_engine)


ORM(Country, new_engine).insert(sakila_country.select())
ORM(City, new_engine).insert(sakila_city.select())
ORM(Address, new_engine).insert(sakila_address.select())


COUNTRY_TO_DEL = "Afghanistan"


address = ORM(Address, new_engine).where(Address.City.Country.country == COUNTRY_TO_DEL).delete()
city = ORM(City, new_engine).where(City.Country.country == COUNTRY_TO_DEL).delete()
country = ORM(Country, new_engine).where(Country.country == COUNTRY_TO_DEL).delete()
pass