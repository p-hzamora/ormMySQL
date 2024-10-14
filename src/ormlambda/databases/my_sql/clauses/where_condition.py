from typing import Any, Callable, Optional, override, Type
import inspect

from ormlambda.common.enums import ConditionType
from ormlambda.utils.lambda_disassembler.tree_instruction import TreeInstruction, TupleInstruction
from ormlambda.common.interfaces.IQueryCommand import IQuery
from ormlambda.components.where.abstract_where import AbstractWhere
from ormlambda import Table


class WhereConditionByArg[TProp1, TProp2](IQuery):
    def __init__(self, cond1: TProp1, cond2: TProp2, symbol: ConditionType) -> None:
        self.cond1: TProp1 = cond1
        self.cond2: TProp2 = cond2
        self.symbol: ConditionType = symbol

    @property
    def query(self) -> str:
        return f"WHERE {self.cond1} {self.symbol.value} {self.cond2}"


class WhereCondition[T: Type[Table], *Inst](AbstractWhere):
    """
    The purpose of this class is to create 'WHERE' condition queries properly.

    Args.
        - instances: tuple[*Inst],
            - passed all instance that we are going to use inside of `function` arg

        - function: Callable[[*Inst], bool] = lambda: None,
            - lambda function to create condition between instance variables
        - **kwargs: Any,
            - We use this clause by passing all the variables that we want to replace inside the lambda function.
            When we try to disassemble the lambda function, we see that the variables were not replaced by their values.
            Instead, we only got the variable names, not the values.
            Due to this problem, we need to specify the correct dictionary to map variable names to their values.

    >>> var = 100
    >>> _lambda = lambda a: a.city_id <= var
    >>> ... #Dissamble _lambda method
    >>> parts_of_lambda = [
    >>>     "city_id"
    >>>     "<="
    >>>     "var"                   <-------- We excepted 100
    >>> ]
    """

    __slots__ = [
        "_instances",
        "_function",
        "_tree",
        "_kwargs",
        "_lambda_param_map",
    ]

    def __init__(
        self,
        instances: tuple[*Inst],
        function: Callable[[*Inst], bool] = lambda: None,
        **kwargs: Any,
    ) -> None:
        self._instances: tuple[Table] = instances
        self._function: Callable[[*Inst], bool] = function
        self._kwargs: dict[str, tuple[*Inst]] = kwargs
        self._tree: TreeInstruction = TreeInstruction(function)
        self._lambda_param_map: dict[str, Table] = self._create_lambda_param_map()

    def _create_lambda_param_map(self) -> dict[str, Table]:
        """
        The method is responsible for mapping the variables present in the lambda function so that they are replaced with the instance of the model Table.
        """
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
        conditions, compare_sign = self.create_conditions_list_and_compare_sign()
        c1, c2 = conditions
        return f"{self.WHERE} {c1} {compare_sign[0]} {c2}"

    def _replace_values(self, ti: TupleInstruction) -> str:
        instance: Any = self._kwargs[ti.var]
        if isinstance(instance, Table):
            data = getattr(instance, ti.nested_element.name)
        else:
            data = instance

        return f"'{data}'" if isinstance(data, str) else data

    def _build_with_lambda_as_condition(self) -> Callable[[], Any]:
        n: int = len(self._tree.compare_op)
        dicc_selector: dict[int, Callable[[], str]] = {
            1: self.__one_sign,
            2: self.__two_sign,
        }
        return dicc_selector[n]()

    def __one_sign(self) -> str:
        """lambda x: x <= 10"""
        (c1, c2), _ = self.create_conditions_list_and_compare_sign()

        return f"{self.WHERE} {c1} {self._tree.compare_op[0]} {c2}"

    def _get_table_for_tuple_instruction(self, ti: TupleInstruction) -> Optional[Table]:
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
        """lambda x: 100 <= x <= 500"""
        self.__valid_between_comparable_sign()
        conds, _ = self.create_conditions_list_and_compare_sign()
        c1, c2, c3 = conds
        cond1 = WhereConditionByArg[str, str](c1, c2, ConditionType(self._tree.compare_op[0]))
        cond2 = WhereConditionByArg[str, str](c2, c3, ConditionType(self._tree.compare_op[1]))

        return WhereCondition.join_condition(cond1, cond2, restrictive=True)

    def __valid_between_comparable_sign(self) -> bool:
        if not len(self._tree.compare_op) == 2:
            raise Exception("Number of comparable signs distinct from 2.")
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

    @override
    def get_involved_tables(self) -> tuple[tuple[Table, Table]]:
        return_involved_tables: list[tuple[Table, Table]] = []
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
            tbl = involved_tables[-1]
            attr = get_attr_tbl(tbl, tbl_name)
            if attr is not None:
                involved_tables.append(attr)
                return_involved_tables.append(tuple([tbl, attr]))
        return tuple(return_involved_tables)

    def create_conditions_list_and_compare_sign(self) -> tuple[list[str], list[str]]:
        compare_sign: list[str] = []
        conds: list[str] = []
        for ti in self._tree.to_list():
            key = ti.var
            ne = ti.nested_element

            if hasattr(ConditionType, str(ne.name)):
                cond_type: ConditionType = getattr(ConditionType, ne.name)
                compare_sign.append(cond_type.value)

            elif key in self._kwargs:
                conds.append(self._replace_values(ti))
            else:
                _name_table = self._get_table_for_tuple_instruction(ti)
                _name_table_str = f"{_name_table}." if _name_table else ""

                _name = ne.name
                if not _name_table:
                    _name = self._wrapp_condition_id_str(ne.name)

                conds.append(f"{_name_table_str}{_name}")
        return conds, compare_sign

    def _wrapp_condition_id_str(self, name: Any):
        if not name:
            return "NULL"
        if not isinstance(name, str):
            return name
        return f"'{name}'"
