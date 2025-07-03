# Apply visitor pattern

from __future__ import annotations
import abc
from typing import TYPE_CHECKING, ClassVar
import operator

if TYPE_CHECKING:
    ...


class Visitor(abc.ABC):
    """
    Abstract base class for all visitors in the SQL AST.
    """

    ensure_kwarg: ClassVar[str] = r"visit_\w+"

    ...


class Element:
    """
    Base class for all elements in the SQL AST.
    """

    __slots__ = ()

    __visit_name__: ClassVar[str]
    """
    The name of the element used for dispatching in the visitor pattern.
    This should be a string that uniquely identifies the type of element.
    """

    if TYPE_CHECKING:

        def _compiler_dispatch(self, visitor: Visitor, **kw) -> str:
            """
            Dispatches the visitor to the appropriate method based on the type of the element.
            """
            ...

    @classmethod
    def __init_subclass__(cls):
        if "__visit_name__" in cls.__dict__:
            cls._generate_compiler_dispatch()
        return super().__init_subclass__()

    @classmethod
    def _generate_compiler_dispatch(cls):
        """
        Generates the _compiler_dispatch method for the class.
        """
        visit_name = cls.__visit_name__

        if not isinstance(visit_name, str):
            raise TypeError(f"__visit_name__ must be a string, not {type(visit_name).__name__}")

        name = f"visit_{visit_name}"
        getter = operator.attrgetter(name)

        def _compiler_dispatch(self, visitor: Visitor, **kw) -> str:
            """
            Dispatches the visitor to the appropriate method based on the type of the element.
            """
            try:
                meth = getter(visitor)
                return meth(self, **kw)

            except AttributeError as err:
                raise err
                # return visitor.visit_unsupported_compilation(self, err, **kw)  # type: ignore  # noqa: E501

        cls._compiler_dispatch = _compiler_dispatch

    def __repr__(self):
        return f"{Element.__name__}: {self.__visit_name__}"
