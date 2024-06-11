from datetime import datetime

import dbcontext as db

from orm import MySQLRepository, IRepositoryBase

from orm.condition_types import ConditionType
from test.models import AddressModel

from dotenv import load_dotenv

load_dotenv()


USERNAME = "root"  # os.getenv("DB_USERNAME")
PASSWORD = "1234"  # os.getenv("DB_PASSWORD")
HOST = "localhost"  # os.getenv("DB_HOST")


# db_common = MySQLRepository(user=USERNAME, password=PASSWORD, database="common", host=HOST).connect()

database: IRepositoryBase = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST).connect()

address = db.Address(address_id=10)

a_model = AddressModel(database)

pattern = r"^A"

filtro = a_model.where(lambda a: 1<= a.city.country.country_id <= 10, pattern=pattern).select(lambda a: (a.city.country.country_id, a.city), flavour=dict)

pass
