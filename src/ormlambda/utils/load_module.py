import logging
import importlib
from typing import Any, Optional

log = logging.getLogger(__name__)


def __load_module__(module_path: str, dialect_name: Optional[str] = None) -> Optional[Any]:
    """
    Load a module by its path and return the module object.
    Returns None if the module cannot be imported
    Args:
        module_path: The dot-separated path to the module

    Returns:
        The loaded module or None if import fails
    """
    try:
        return importlib.import_module(module_path)
    except ImportError:
        log.error(f"{module_path.split('.')[-1] if not dialect_name else dialect_name} dialect not available")
