"""Regression tests: unfinished update plumbing must never claim success."""
from core.updater import UpdateManager


def test_updater_rejects_placeholder_download(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    updater = UpdateManager()
    assert updater.download_update("https://example.invalid/fake.tar.gz") is False
    assert not list(tmp_path.rglob("*.tar.gz"))


def test_updater_rejects_placeholder_install(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    updater = UpdateManager()
    fake_archive = tmp_path / "not-an-update.tar.gz"
    assert updater.install_update(str(fake_archive)) is False
    assert not fake_archive.exists()
