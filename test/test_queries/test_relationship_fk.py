import sys
from decouple import config
from pathlib import Path
import unittest
import importlib.util

USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")

sys.path = [str(Path(__file__).parent.parent.parent), *sys.path]

from orm.utils import ForeignKey, Table  # noqa: E402


def load_module(m_name: str, m_path: Path):
    spec = importlib.util.spec_from_file_location(m_name, m_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[m_name] = module
    return module


def _path(n: str) -> Path:
    return Path(__file__).parent.parent / "models" / f"{n}.py"


class TestForeignKey(unittest.TestCase):
    def setUp(self) -> None:
        ForeignKey.MAPPED.clear()

    def tearDown(self) -> None:
        loop = ("country", "city", "address", "store", "staff")

        for name in loop:
            _name = f"models.{name}"
            if sys.modules.get(_name):
                del sys.modules[_name]

    def test_fk_empty_if_not_modules(self):
        self.assertDictEqual(ForeignKey.MAPPED, {})

    def test_fk_with_staff_table_in_imports(self):
        _ = load_module("models.country", _path("country")).Country
        City: Table = load_module("models.city", _path("city")).City
        Address: Table = load_module("models.address", _path("address")).Address
        Store: Table = load_module("models.store", _path("store")).Store
        Staff: Table = load_module("models.staff", _path("staff")).Staff

        map = {
            City: ...,
            Address: ...,
            Store: ...,
            Staff: ...,
        }

        self.assertTupleEqual(tuple(ForeignKey.MAPPED), tuple(map))

    def test_if_fk_replace_table_name_by_table_object(self):
        """
        Testing if ForeignKey.MAPPED replaces 'str' keys with 'Table' object only when the keys match the table name of the 'Table' obejct they are being replaced by.
        """
        ForeignKey[Table, Table].MAPPED["city"] = {}

        self.assertIn("city", ForeignKey.MAPPED)

        _ = load_module("models.country", _path("country")).Country
        City = load_module("models.city", _path("city")).City

        self.assertIsNone(ForeignKey.MAPPED.get("city", None), None)
        self.assertIn(City, ForeignKey.MAPPED)


if __name__ == "__main__":
    unittest.main()
