from typing import Any, Callable, override

from orm.condition_types import ConditionType
from orm.dissambler.nested_element import NestedElement
from orm.dissambler.tree_instruction import TreeInstruction
from orm.interfaces.IQuery import IQuery
from orm.orm_objects.table.table_constructor import Table


class WhereConditionByArg[TProp1, TProp2](IQuery):
    def __init__(self, cond1: TProp1, cond2: TProp2, symbol: ConditionType) -> None:
        self.cond1: TProp1 = cond1
        self.cond2: TProp2 = cond2
        self.symbol: ConditionType = symbol

    @property
    def query(self) -> str:
        return f"WHERE {self.cond1} {self.symbol.value} {self.cond2}"


class WhereCondition[*Inst](IQuery):
    WHERE: str = "WHERE"
    __slots__ = [
        "_instances",
        "_function",
        "_tree",
    ]

    def __init__(self, function: Callable[[*Inst], bool], **kwargs: Any) -> None:
        self._function: Callable[[*Inst], bool] = function
        self._kwargs: dict[str, tuple[*Inst]] = kwargs

        self._tree: TreeInstruction = TreeInstruction(function)

    @override
    @property
    def query(self) -> str:
        if len(self._tree.compare_op) == 0:
            return self._build_with_lambda_as_column_name()
        return self._build_with_lambda_as_condition()

    def _build_with_lambda_as_column_name(self) -> str:
        conditions = []
        compare_sign = []
        for lkey, nested_element in self._tree.to_dict().items():
            if nested_element.name in ConditionType._value2member_map_:
                compare_sign.append(nested_element.name)

            elif lkey in self._kwargs:
                conditions.append(self._replace_values(lkey, nested_element))

            else:
                conditions.append(f"{nested_element.name}")

        c1, c2 = conditions

        return f"{self.WHERE} {c1} {compare_sign[0]} {c2}"

    def _replace_values(self, _lambda_key: str, _nested_element: NestedElement):
        instance = self._kwargs[_lambda_key]
        if isinstance(instance, Table):
            return getattr(instance, _nested_element.name)
        else:
            return instance

    def _build_with_lambda_as_condition(self) -> Callable[[], Any]:
        n: int = len(self._tree.compare_op)
        dicc_selector: dict[int, Callable[[], str]] = {
            1: self.__one_sign,
            2: self.__two_sign,
        }
        return dicc_selector[n]()

    def __one_sign(self) -> str:
        conds = []
        for x in self._tree.to_list():
            ne = x.nested_element
            if x.var in self._kwargs:
                conds.append(self._replace_values(x.var, ne))
            else:
                conds.append(ne.name)

        c1, c2 = conds
        return f"{self.WHERE} {c1} {self._tree.compare_op[0]} {c2}"

    def __two_sign(self) -> str:
        self.__valid_between_comparable_sign()

        conds = []
        for key, nested_element in self._tree.to_dict().items():
            if key in self._kwargs:
                conds.append(self._replace_values(key, nested_element))
            else:
                conds.append(nested_element.name)

        c1, c2, c3 = conds
        cond1 = WhereConditionByArg[str, str](c1, c2, ConditionType(self._tree.compare_op[0]))
        cond2 = WhereConditionByArg[str, str](c2, c3, ConditionType(self._tree.compare_op[1]))

        return WhereCondition.join_condition(cond1, cond2, restrictive=True)

    def __valid_between_comparable_sign(self) -> bool:
        if len(self._tree.compare_op) > 2:
            raise Exception("Number of comparable signs greater than 2.")
        return True

    @classmethod
    def join_condition(cls, *args: WhereConditionByArg, restrictive=False) -> str:
        BY: str = "AND" if restrictive else "OR"
        query: str = f"{cls.WHERE} "

        n = len(args)
        for i in range(n):
            condition: IQuery = args[i]
            query += "(" + condition.query.removeprefix(f"{cls.WHERE} ") + ")"
            if i != n - 1:
                query += f" {BY} "

        return query
