from ormlambda.caster import BaseCaster, PLACEHOLDER
from shapely import Point
import shapely.wkt as wkt
from shapely import wkb


class PointCaster[TType](BaseCaster[Point, TType]):
    def __init__(self, value: bytes | str, type_value: TType):
        super().__init__(value, type_value)

    @property
    def wildcard_to_select(self) -> str:
        return f"ST_AsText({PLACEHOLDER})"

    @property
    def wildcard_to_where(self) -> str:
        return f"ST_AsText({PLACEHOLDER})"

    @property
    def wildcard_to_insert(self) -> str:
        return f"ST_GeomFromText({PLACEHOLDER})"

    @property
    def to_database(self) -> str:
        if isinstance(self.value, Point):
            return self.value.wkt
        return self.value

    @property
    def from_database(self) -> Point:
        """
        Always should get string because we're using 'ST_AsText' when calling wildcard_to_select prop.
        """
        if isinstance(self.value, bytes):
            return wkb.loads(self.value)
        elif isinstance(self.value, str):
            return wkt.loads(self.value)
        return self.value

    @property
    def string_data(self)->str:
        
        return type(self)(str(self.value),str).wildcard_to_select