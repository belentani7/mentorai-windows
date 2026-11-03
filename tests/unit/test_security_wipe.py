"""Regression: local-data deletion must never follow a symlink outside MentorAI."""
from pathlib import Path

import pytest

from core.security_manager import SecurityManager


def _symlink_or_skip(link: Path, target: Path, *, directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"Symlinks unavailable on this test host: {exc}")


def test_file_symlink_removes_link_without_overwriting_external_file(tmp_path):
    external = tmp_path / "personal.txt"
    external.write_bytes(b"PRIVATE USER FILE")
    data_dir = tmp_path / "mentorai"
    data_dir.mkdir()
    link = data_dir / "master.key"
    _symlink_or_skip(link, external)

    SecurityManager._best_effort_delete(link)

    assert external.read_bytes() == b"PRIVATE USER FILE"
    assert not link.is_symlink()


def test_directory_symlink_does_not_delete_external_directory(tmp_path):
    external = tmp_path / "personal-folder"
    external.mkdir()
    (external / "family.txt").write_text("keep", encoding="utf-8")
    data_dir = tmp_path / "mentorai"
    data_dir.mkdir()
    link = data_dir / "fake-database"
    _symlink_or_skip(link, external, directory=True)

    SecurityManager._best_effort_delete(link)

    assert (external / "family.txt").read_text(encoding="utf-8") == "keep"
    assert not link.is_symlink()


def test_broken_symlink_is_removed(tmp_path):
    link = tmp_path / "master.key"
    _symlink_or_skip(link, tmp_path / "nonexistent")

    SecurityManager._best_effort_delete(link)

    assert not link.is_symlink()


def test_regular_file_is_removed(tmp_path):
    target = tmp_path / "mentorai.db"
    target.write_bytes(b"encrypted local database")
    SecurityManager._best_effort_delete(target)
    assert not target.exists()


def test_regular_directory_is_removed(tmp_path):
    target = tmp_path / "mentorai"
    target.mkdir()
    (target / "history.db").write_bytes(b"encrypted local database")
    SecurityManager._best_effort_delete(target)
    assert not target.exists()
