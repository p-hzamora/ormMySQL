from typing import Any, Callable, Optional, override
import inspect
from orm.condition_types import ConditionType
from orm.dissambler.nested_element import NestedElement
from orm.dissambler.tree_instruction import TreeInstruction, TupleInstruction
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
        "_kwargs",
        "_lambda_param_map",
    ]

    def __init__(self, instances: tuple[*Inst], function: Callable[[*Inst], bool] = lambda: None, **kwargs: Any) -> None:
        self._instances: tuple[Table] = instances
        self._function: Callable[[*Inst], bool] = function
        self._kwargs: dict[str, tuple[*Inst]] = kwargs
        self._tree: TreeInstruction = TreeInstruction(function)
        self._lambda_param_map: dict[str, Table] = self._create_lambda_param_map()

    def _create_lambda_param_map(self) -> dict[str, Table]:
        assert len(lamda_param := inspect.signature(self._function).parameters) == len(self._instances)

        _temp_instances = list(self._instances)[::-1]  # we copied and translated tuple instance due to pop each value in order to param
        new_dicc: dict[str, Table] = {}
        for param in lamda_param.keys():
            new_dicc[param] = _temp_instances.pop()

        return new_dicc

    @override
    @property
    def query(self) -> str:
        if len(self._tree.compare_op) == 0:
            return self._build_with_lambda_as_column_name()
        return self._build_with_lambda_as_condition()

    def _build_with_lambda_as_column_name(self) -> str:
        conditions = []
        compare_sign = []
        for ti in self._tree.to_list():
            lkey = ti.var
            nested_element = ti.nested_element
            if nested_element.name in ConditionType._value2member_map_:
                compare_sign.append(nested_element.name)

            elif lkey in self._kwargs:

                conditions.append(self._replace_values(lkey, nested_element))

            else:
                _name_table = self._get_table_for_tuple_instruction(ti)
                if _name_table:
                    _name_table = f"{_name_table}."
                conditions.append(f"{_name_table if _name_table else ""}{nested_element.name}")

        c1, c2 = conditions
        return f"{self.WHERE} {c1} {compare_sign[0]} '{c2}'"

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
        for ti in self._tree.to_list():
            ne = ti.nested_element
            if ti.var in self._kwargs:
                conds.append(self._replace_values(ti.var, ne))
            else:
                _name_table = self._get_table_for_tuple_instruction(ti)
                if _name_table:
                    _name_table = f"{_name_table}."
                conds.append(f"{_name_table if _name_table else ""}{ne.name}")

        c1, c2 = conds

        return f"{self.WHERE} {c1} {self._tree.compare_op[0]} {c2}"

    def _get_table_for_tuple_instruction(self, ti: TupleInstruction)->Optional[Table]:
        if ti.var not in self._lambda_param_map:
            return None
        
        involved_tables: list[Table] = [self._lambda_param_map[ti.var]]

        def get_attr_tbl(tbl: Table, class_var: str) -> Optional[Table]:
            tbl_attrs = (tbl, class_var)
            if hasattr(*tbl_attrs):
                attr = getattr(*tbl_attrs)

                if not isinstance(attr, property) and issubclass(attr, Table):
                    return attr
            return None

        for name in ti.nested_element.parents[1:]:
            attr = get_attr_tbl(involved_tables[-1], name)
            if attr is not None:
                involved_tables.append(attr)

        return involved_tables[-1].__table_name__

    def __two_sign(self) -> str:
        self.__valid_between_comparable_sign()

        conds = []
        for ti in self._tree.to_list():
            key =ti.var
            ne =ti.nested_element
            if key in self._kwargs:
                conds.append(self._replace_values(key, ne))
            else:
                _name_table = self._get_table_for_tuple_instruction(ti)
                if _name_table:
                    _name_table = f"{_name_table}."
                conds.append(f"{_name_table if _name_table else ""}{ne.name}")

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

    def get_involved_tables(self) -> list[Table]:
        involved_tables: list[Table] = [self._instances[0]]

        def get_attr_tbl(instance: Table, tbl_name: str) -> Optional[Table]:
            inst_tbl_name = (instance, tbl_name)
            if hasattr(*inst_tbl_name):
                attr = getattr(*inst_tbl_name)

                if not isinstance(attr, property) and issubclass(attr, Table):
                    return attr
            return None

        tables: list[str] = self._tree.to_list()[0].nested_element.parents[1:]  # Avoid lambda variable
        for tbl_name in tables:
            attr = get_attr_tbl(involved_tables[-1], tbl_name)
            if attr is not None:
                involved_tables.append(attr)
        return involved_tables
