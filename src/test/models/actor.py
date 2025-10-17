import sys
from pathlib import Path

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda import Column, Table

from datetime import datetime

from typing import Annotated
from ormlambda import PrimaryKey


class Actor(Table):
    __table_name__ = "actor"

    actor_id: Annotated[Column[str], PrimaryKey()] = Column(int, is_primary_key=True)
    first_name: Column[str]
    last_name: Column[str]
    last_update: Column[datetime]
