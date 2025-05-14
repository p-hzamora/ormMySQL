from __future__ import annotations
from typing import Optional, Any, TYPE_CHECKING

from .visitors import Element

if TYPE_CHECKING:
    from ormlambda.engine.base import Engine
    from ormlambda.dialects import Dialect
    from .compiler import Compiled


class CompilerElement(Element):
    """
    Base class for all compiler elements in SQLAlchemy.
    """

    __slots__ = ()
    __visit_name__ = "compiler_element"

    def compile(
            self,
            bind:Optional[Engine]=None,
            dialect:Optional[Dialect]=None,
            **kw:Any)->Compiled:
        
        if dialect is None:
            if bind is None:
                raise TypeError("Either bind or dialect must be provided.")
            dialect = bind.dialect
        return self._compiler(dialect, **kw)
    

    def _compiler(self,dialect:Dialect, **kw:Any)->Compiled:
        """
        Compile the element into a SQL string.
        """
        return dialect.statement_compiler(dialect,self, **kw)
    
class ClauseElement(CompilerElement):
    """
    Base class for all clause elements in SQLAlchemy.
    """

    __visit_name__ = "clause_element"

