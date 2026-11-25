from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_repo_exists():
    assert True


def test_key_paths_exist():
    assert (ROOT / "README.md").is_file()
    assert (ROOT / "requirements-windows.txt").is_file()
    assert (ROOT / "knowledge_base").is_dir()
    assert (ROOT / "core" / "assistant_engine.py").is_file()
    assert (ROOT / "ui" / "mentorai_windows_ui.py").is_file()
