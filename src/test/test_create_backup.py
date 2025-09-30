import sys
from pathlib import Path
import unittest
import io

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from test.config import create_sakila_engine
from test.env import TEST_DIR

CREATED_FILES: set[Path] = set()


def delete_files_in(path: Path) -> None:
    for file in path.iterdir():
        file.unlink()
    path.rmdir()
    return None


def count_files_in_(path: Path) -> int:
    return len(list(path.iterdir()))


class BackupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_sakila_engine()

    def setUp(self):
        self.OUTPUT = TEST_DIR / "backups"

        if self.OUTPUT.exists():
            delete_files_in(self.OUTPUT)

        self.OUTPUT.mkdir(exist_ok=False)

    @classmethod
    def tearDownClass(cls):
        for folder in CREATED_FILES:
            delete_files_in(folder)

    def test_backup_auto_generated(self) -> None:
        self.assertEqual(count_files_in_(self.OUTPUT), 0)
        backup = self.engine.create_backup()
        self.assertEqual(backup.exists(), True)
        CREATED_FILES.add(backup.parent)

    def test_custom_file_path(self):
        CUSTOM_PATH = TEST_DIR / "custom_path" / "custom_backup.sql"
        self.assertEqual(CUSTOM_PATH.exists(), False)
        backup = self.engine.create_backup(output=CUSTOM_PATH)
        self.assertEqual(backup.exists(), True)
        CREATED_FILES.add(backup.parent)

    def test_compressed_file(self):
        backup = self.engine.create_backup(compress=True)
        self.assertEqual(backup.exists(), True)
        CREATED_FILES.add(backup.parent)

    # def test_string_stream(self):
    #     string_stream = io.StringIO()
    #     backup_data = self.engine.create_backup(output=string_stream)
    #     print("Backup size:", len(string_stream.getvalue()))

    def test_binary_stream(self):
        binary_stream = io.BytesIO()
        backup = self.engine.create_backup(output=binary_stream, compress=True)
        self.assertIsInstance(backup, bytes)

    # def test_standard_output(self):
    #     self.engine.create_backup(output=sys.stdout)


if __name__ == "__main__":
    unittest.main()
