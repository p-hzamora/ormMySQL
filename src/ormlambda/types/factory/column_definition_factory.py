from __future__ import annotations
import logging
from typing import ClassVar, Optional, Type, TYPE_CHECKING

from ormlambda.types import DatabaseType
from ormlambda.utils import __load_module__

if TYPE_CHECKING:
    from ..renderers.column_renderer import ColumnDefinitionRenderer


log = logging.getLogger(__name__)


class ColumnDefinitionFactory:
    _renderers: ClassVar[dict[Optional[DatabaseType], Type[ColumnDefinitionRenderer]]] = {}
    _default_renderer: ClassVar[Optional[Type[ColumnDefinitionRenderer]]] = None
    _initialized: ClassVar[bool] = False

    @classmethod
    def initialize(cls) -> None:
        """Initialize the factory by importing renderers"""

        if cls._initialized:
            return None

        # Import column definition renderers
        try:
            __load_module__("ormlambda.types.dialects.default.columns", "Default")
            __load_module__("ormlambda.types.dialects.sqlite.columns", "SQLite")
            __load_module__("ormlambda.types.dialects.mysql.columns", "MySQL")
            __load_module__("ormlambda.types.dialects.postgresql.columns", "PostgreSQL")

            # Print debug info
            log.debug(f"Initialized {ColumnDefinitionFactory.__name__} with:")
            log.debug(f"- {len(cls._renderers)} dialect-specific renderers")
            log.debug(f"- {cls._default_renderer.__name__} default renderers")

            cls._initialized = True

        except ImportError as e:
            log.error(f"Error initializing {ColumnDefinitionFactory.__name__}: {e}")

    @classmethod
    def register_renderer(cls, dialect: Optional[DatabaseType], renderer_class: Type[ColumnDefinitionRenderer]) -> None:
        """"""
        cls._renderers[dialect] = renderer_class

    @classmethod
    def register_default_renderer(cls, renderer_class: Type[ColumnDefinitionRenderer]) -> None:
        """"""
        cls._default_renderer = renderer_class

    @classmethod
    def get_renderer(cls, dialect: Optional[DatabaseType]) -> ColumnDefinitionRenderer:
        """"""
        if not cls._initialized:
            cls.initialize()

        if dialect and dialect in cls._renderers:
            return cls._renderers[dialect]()

        if cls._default_renderer:
            return cls._default_renderer()

        from ..dialects.default.columns import DefaultColumnDefinitionRenderer

        return DefaultColumnDefinitionRenderer()
