import unittest
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent))
from orm import Table, Column, ForeignKey
from orm import ModelBase
from orm import nameof
from orm import MySQLRepository, IRepositoryBase


class City(Table):
    __table_name__: str = "city"

    def __init__(
        self,
        pk_city: int,
        literal: str,
    ) -> None:
        self._pk_city: Column[int] = Column(nameof(pk_city), pk_city, is_primary_key=True)
        self._literal: Column[int] = Column(nameof(literal), literal, is_unique=True)

    @property
    def pk_city(self):
        return self._pk_city.column_value

    @pk_city.setter
    def pk_city(self, value):
        self._pk_city.column_value = value

    @property
    def literal(self):
        return self._literal.column_value

    @literal.setter
    def literal(self, value):
        self._literal.column_value = value


class Person(Table):
    __table_name__ = "person"

    def __init__(
        self,
        id: int,
        title: int,
        content: int,
        dni_list: list,
        fk_city: City,
    ) -> None:
        self._id: Column[int] = Column(nameof(id), id, is_primary_key=True)
        self._title: Column[int] = Column(nameof(title), title)
        self._content: Column[int] = Column(nameof(content), content)
        self._dni_list: Column[list] = Column(nameof(dni_list), str(dni_list))
        self._fk_city: Column[list] = Column(nameof(fk_city), str(fk_city))
        
        self.city: ForeignKey[City] = ForeignKey(nameof(City.pk_city), nameof(fk_city), str(fk_city), modelbase="common")

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

    def __init__(self, methodName: str = "SQLMapping") -> None:
        super().__init__(methodName)

    def test_create_orm(self):
        mysql = MySQLRepository("root", "1234", "db").connect()
        model = PersonModelBase(mysql)
        model.first().fk_city.literal


if "__main__" == __name__:
    unittest.main()
