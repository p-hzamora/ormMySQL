from datetime import datetime
import dbcontext as db

from orm import MySQLRepository, IRepositoryBase

from orm.condition_types import ConditionType
from test.models import AddressModel
from test.models.store import StoreModel, Store

from dotenv import load_dotenv

load_dotenv()


USERNAME = "root"  # os.getenv("DB_USERNAME")
PASSWORD = "1234"  # os.getenv("DB_PASSWORD")
HOST = "localhost"  # os.getenv("DB_HOST")


# db_common = MySQLRepository(user=USERNAME, password=PASSWORD, database="common", host=HOST).connect()

database: IRepositoryBase = MySQLRepository(user=USERNAME, password=PASSWORD, database="sakila", host=HOST).connect()

address = db.Address(address_id=10)

a_model = AddressModel(database)


filter_by_address_id = a_model.where(lambda x: x.address_id == 1).select()

store = Store(None,3,603,datetime.now())
a = StoreModel(database).insert(store)

a_model.where(lambda x: x.address_id == 3).delete()

pass
