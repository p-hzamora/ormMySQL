import unittest
import sys
import os
from pathlib import Path
import dotenv


sys.path = [str(Path(__file__).parent.parent), *sys.path]


from orm import Table, Column, ForeignKey  # noqa: E402
from orm import ModelBase  # noqa: E402
from orm import MySQLRepository, IRepositoryBase  # noqa: E402
from test.models import City  # noqa: E402

dotenv.load_dotenv()


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


class Person(Table):
    __table_name__ = "person"

    def __init__(
        self,
        title: str,
        content: str,
        dni_list: list,
        fk_city: int,
        id: int = None,
    ) -> None:
        self._id: int = Column[int](id, is_primary_key=True, is_auto_increment=True)
        self._title: str = Column[str](title)
        self._content: str = Column[str](content)
        self._dni_list: list = Column[list](str(dni_list))
        self._fk_city: int = Column[int](str(fk_city))

        self.city: ForeignKey[Person, City] = ForeignKey[Person, City](
            orig_table=Person,
            referenced_table=City,
            relationship=lambda p, c: p.fk_city == c.city_id,
            # referenced_database="common",
        )

    @property
    def id(self):
        return self._id.column_value

    @id.setter
    def id(self, value):
        self._id.column_value = value

    @property
    def title(self):
        return self._title.column_value

    @title.setter
    def title(self, value):
        self._title.column_value = value

    @property
    def content(self):
        return self._content.column_value

    @content.setter
    def content(self, value):
        self._content.column_value = value

    @property
    def dni_list(self):
        return eval(self._dni_list.column_value)

    @dni_list.setter
    def dni_list(self, value):
        self._dni_list.column_value = str(value)

    @property
    def fk_city(self):
        return self._fk_city.column_value

    @fk_city.setter
    def fk_city(self, value):
        self._fk_city.column_value = value


class PersonModelBase(ModelBase[Person]):
    def __init__(self, repository: IRepositoryBase):
        super().__init__(Person, repository=repository)


class TestSQLMapping(unittest.TestCase):
    PERSON_INSTANCE: Person = Person(1, "titleCustom", "contentCustom", [1, 2, 3, 4, 5, 6], "Cantabria")

    def test_create_orm(self):
        mysql = MySQLRepository(USERNAME, PASSWORD, "sakila").connect()
        person = Person("titulo", "contenido", [1, 2, 3, 4], 2)
        person_model = PersonModelBase(mysql)
        city = person_model.filter_by(person).first(lambda x: x.city)
        city


if "__main__" == __name__:
    unittest.main()
