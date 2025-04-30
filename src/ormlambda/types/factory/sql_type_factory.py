from __future__ import annotations
from typing import ClassVar, Optional, Type
import logging
from ..base import DatabaseType
from ..sql_type import SQLType
from ..renderers.sql_type_renderer import SQLTypeRenderer
from ormlambda.utils import __load_module__

log = logging.getLogger(__name__)

type RenderersType = dict[tuple[Optional[DatabaseType], Type[SQLType]], Type[SQLTypeRenderer]]


class SQLTypeRendererFactory:
    """Factory for SQL type renderers following the Factory pattern"""

    _renderers: RenderersType = {}
    _default_renderers: dict[Type[SQLType], Type[SQLTypeRenderer]] = {}
    _initialized: ClassVar[bool] = False

    @classmethod
    def initialize(cls) -> None:
        """Initialize the factory by importing dialect"""
        if cls._initialized:
            return None

        # Import column definition renderers
        try:
            __load_module__("ormlambda.types.dialects.default.sql_types", "Default")
            __load_module__("ormlambda.types.dialects.sqlite.sql_types", "SQLite")
            __load_module__("ormlambda.types.dialects.mysql.sql_types", "MySQL")
            __load_module__("ormlambda.types.dialects.postgresql.sql_types", "PostgreSQL")

            # Print debug info
            log.debug(f"Initialized {SQLTypeRendererFactory.__name__} with:")
            log.debug(f"- {len(cls._renderers)} dialect-specific renderers")
            log.debug(f"- {len(cls._default_renderers)} default renderers")

            cls._initialized = True

        except ImportError as e:
            log.error(f"Error initializing {SQLTypeRendererFactory.__name__}: {e}")

    @classmethod
    def register_renderer(cls, dialect: Optional[DatabaseType], sql_type_class_name: str, renderer_class: Type[SQLTypeRenderer]) -> None:
        """Register a renderer for a specific dialect and SQL type"""
        cls._renderers[(dialect, sql_type_class_name)] = renderer_class

    @classmethod
    def register_default_renderer(cls, sql_type_class_name: str, renderer_class: Type[SQLTypeRenderer]) -> None:
        """Register a default renderer for a SQL type (used when no dialect-specific renderer exists)"""
        cls._default_renderers[sql_type_class_name] = renderer_class

    @classmethod
    def get_renderer(cls, dialect: Optional[DatabaseType], sql_type_class: Type[SQLType]) -> SQLTypeRenderer:
        """Get the appropiate renderer for a dialect and SQL type.
        Falls back to default renderer if no dialect-specific renderer exists"""

        if not cls._initialized:
            cls.initialize()

        sql_type_class_name = sql_type_class.__name__

        if (key := (dialect, sql_type_class_name)) in cls._renderers:
            return cls._renderers[key]()

        for base_class in sql_type_class.__mro__[1:]:
            if issubclass(base_class, SQLType) and (key := (dialect, base_class)) in cls._renderers:
                return cls._renderers[key]()

        if sql_type_class_name in cls._default_renderers:
            return cls._default_renderers[sql_type_class]()

        for base_class in sql_type_class.__mro__[1:]:
            if issubclass(base_class, SQLType) and base_class in cls._renderers:
                return cls._default_renderers[base_class]()

        from ..dialects.default.sql_types import DefaultSQLTypeRenderer

        return DefaultSQLTypeRenderer()
