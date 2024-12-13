import typing as tp

from ormlambda.common.abstract_classes.clause_info_context import ClauseInfoContext
from ormlambda.types import ColumnType
from ormlambda.common.abstract_classes.clause_info import AggregateFunctionBase

if tp.TYPE_CHECKING:
    from ormlambda import Table


class Sum[T: tp.Type[Table]](AggregateFunctionBase):
    @staticmethod
    def FUNCTION_NAME() -> str:
        return "Sum"

    def __init__[TProp](
        self,
        column: tuple[ColumnType[TProp]] | ColumnType[TProp],
        alias_name: str = "sum",
        context: tp.Optional[ClauseInfoContext] = None,
    ):
        super().__init__(column, alias_name, context)
