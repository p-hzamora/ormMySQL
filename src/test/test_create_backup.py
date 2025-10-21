from pathlib import Path
import io
from typing import Generator

import pytest


from test.env import TEST_DIR
from ormlambda.engine import Engine

CREATED_FILES: set[Path] = set()


def delete_files_in(path: Path) -> None:
    for file in path.iterdir():
        file.unlink()
    path.rmdir()
    return None


def count_files_in_(path: Path) -> int:
    return len(list(path.iterdir()))


@pytest.fixture
def output() -> Path:
    return TEST_DIR / "backups"


@pytest.fixture
def engine(output: Path, sakila_engine) -> Generator[Engine, None, None]:  # noqa: F811
    if output.exists():
        delete_files_in(output)

    output.mkdir(exist_ok=False)

    yield sakila_engine

    while len(CREATED_FILES) > 0:
        folder = CREATED_FILES.pop()
        delete_files_in(folder)


def test_backup_auto_generated(output: Path, engine: Engine) -> None:
    assert count_files_in_(output) == 0

    backup = engine.create_backup()
    assert backup.exists() is True

    CREATED_FILES.add(backup.parent)


def test_custom_file_path(engine: Engine):
    CUSTOM_PATH = TEST_DIR / "custom_path" / "custom_backup.sql"
    assert CUSTOM_PATH.exists() is False
    backup = engine.create_backup(output=CUSTOM_PATH)
    assert backup.exists() is True
    CREATED_FILES.add(backup.parent)


def test_compressed_file(engine: Engine):
    backup = engine.create_backup(compress=True)
    assert backup.exists() is True
    CREATED_FILES.add(backup.parent)


@pytest.mark.skip("FIXME: backup size print")
def test_string_stream(engine: Engine):
    string_stream = io.StringIO()
    backup_data = engine.create_backup(output=string_stream)
    print("Backup size:", len(string_stream.getvalue()))


def test_binary_stream(engine: Engine):
    binary_stream = io.BytesIO()
    backup = engine.create_backup(output=binary_stream, compress=True)
    assert isinstance(backup, bytes)


@pytest.mark.skip("FIXME: backup size print")
def test_standard_output(engine: Engine):
    import sys

    engine.create_backup(output=sys.stdout)
