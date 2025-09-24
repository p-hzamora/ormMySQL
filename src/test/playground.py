from __future__ import annotations
from datetime import datetime
import sys
from pathlib import Path
from typing import Literal, Optional

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.config import create_sakila_engine
from ormlambda import ORM, Count
from test.models import Address


engine = create_sakila_engine()

CO = "^S"
# fmt: off
result = (
    ORM(Address, engine).offset(3)
            .groupby(lambda x: x.City.Country)
            .where(lambda x: x.City.Country.country.regex(CO))
            .limit(2)
            .order(lambda x: x.City.city, "ASC")
            .select(lambda x: (
                x.City.city,
                Count(x.address_id)
            ),flavour=tuple)
        
)
# fmt: on

pass
