from pathlib import Path
import io


def test_backup_auto_generated(sakila_engine, tmp_path: Path) -> None:
    backup = sakila_engine.create_backup(backup_dir=tmp_path)
    assert backup.exists()


def test_custom_file_path(sakila_engine, tmp_path: Path):
    CUSTOM_PATH = tmp_path / "custom_path" / "custom_backup.sql"
    assert CUSTOM_PATH.exists() is False
    backup = sakila_engine.create_backup(output=CUSTOM_PATH)
    assert backup.exists()


def test_compressed_file(sakila_engine, tmp_path: Path):
    backup = sakila_engine.create_backup(compress=True, backup_dir=tmp_path)
    assert backup.exists()


def test_string_stream(sakila_engine):
    string_stream = io.StringIO()
    sakila_engine.create_backup(output=string_stream)


def test_binary_stream(sakila_engine, tmp_path: Path):
    binary_stream = io.BytesIO()
    backup = sakila_engine.create_backup(output=binary_stream, compress=True, backup_dir=tmp_path)
    assert isinstance(backup, bytes)


def test_standard_output(sakila_engine, tmp_path: Path):
    import sys

    sakila_engine.create_backup(output=sys.stdout)
