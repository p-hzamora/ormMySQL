from ..sql_type import SQLType


class Point(SQLType):
    """Represents a geometric point with X and Y coordinates"""
    
    def __init__(self, srid: int = None, dimensions: int = 2):
        """
        Initialize a Point type
        
        Args:
            srid: Spatial Reference ID (coordinate system)
            dimensions: Number of dimensions (2 for 2D, 3 for 3D with Z, 4 for 4D with Z and M)
        """
        self.srid = srid
        self.dimensions = dimensions

