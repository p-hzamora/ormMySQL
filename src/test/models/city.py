from ormlambda import (
    Column,
    Table,
    ForeignKey,
)

from datetime import datetime

from .country import Country
from ormlambda.sql.sqltypes import VARCHAR, INT, DATETIME


class City(Table):
    __table_name__ = "city"

    city_id: Column[INT] = Column(INT(), is_primary_key=True, is_auto_increment=True, check_types=False)
    city: Column[str] = Column(VARCHAR(50), check_types=False)
    country_id: Column[INT] = Column(INT(), check_types=False)
    last_update: Column[datetime] = Column(DATETIME(), check_types=False)

    Country = ForeignKey["City", Country](Country, lambda ci, co: ci.country_id == co.country_id)
