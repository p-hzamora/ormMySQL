from typing import Callable, Optional
from types import ModuleType
from ormlambda import errors


class PluginLoader:
    def __init__(self, group: str, auto_fn: Optional[Callable[..., ModuleType]] = None):
        self.group = group
        self.impls: dict[str, ModuleType] = {}
        self.auto_fn = auto_fn

    def clear(self):
        self.impls.clear()

    def load(self, name: str) -> Optional[ModuleType]:
        if name in self.impls:
            return self.impls[name]()
        if self.auto_fn:
            loader = self.auto_fn(name)
            if loader:
                self.impls[name] = loader
                return loader()
        raise errors.NoSuchModuleError(f"Can't load plugin: {self.group}:{name}")

    def register(self, name: str, modulepath: str, objname: str) -> None:
        def load():
            mod = __import__(modulepath)
            for token in modulepath.split(".")[1:]:
                mod = getattr(mod, token)
            return getattr(mod, objname)

        self.impls[name] = load
