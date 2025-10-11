from __future__ import annotations
from ormlambda.sql.comparer import ComparerCluster, Comparer
from ormlambda.sql.elements import ClauseElement

from ormlambda.sql.types import UnionType
from ormlambda.common.enums import UnionEnum


class Where(ClauseElement):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.
    """

    __visit_name__ = "where"

    def __init__(self):
        self.comparers: list[ComparerCluster | Comparer] = []
        self.restrictive: list[UnionType] = []

    def add_comparer_tuple(self, tuple_: list[ComparerCluster | Comparer], union: UnionEnum) -> None:
        """If recieve a list we should have minimun 2 elemnts otherwise, whe"""
        n = len(tuple_)
        if n == 1:
            tuple_ = tuple_[0]

            self.restrictive.append(union)
            self.comparers.append(tuple_)
            return None

        cluster = ComparerCluster(tuple_[0], tuple_[1], UnionEnum.AND)
        for i in range(2, n):
            el = tuple_[i]

            cluster = ComparerCluster(cluster, el, UnionEnum.AND)

        self.restrictive.append(union)
        self.comparers.append(cluster)
        return None



__all__ = ["Where"]
