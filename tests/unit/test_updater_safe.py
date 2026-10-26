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


def test_rollback_never_removes_an_existing_app_or_unverified_backup(tmp_path, monkeypatch):
    """A pre-existing backup must not make recursive deletion permissible."""
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    updater = UpdateManager(app_version="1.0.0")

    app_dir = tmp_path / "installed_app"
    app_dir.mkdir()
    (app_dir / "critical.exe").write_bytes(b"installed version")
    updater.app_dir = app_dir

    backup = tmp_path / ".mentorai" / "backup_1.0.0"
    backup.mkdir(parents=True)
    (backup / "critical.exe").write_bytes(b"untrusted backup")

    assert updater.rollback_update() is False
    assert (app_dir / "critical.exe").read_bytes() == b"installed version"
    assert (backup / "critical.exe").read_bytes() == b"untrusted backup"
    assert "Rollback automático bloqueado" in updater.update_log_path.read_text(encoding="utf-8")


def test_auto_updates_cannot_be_enabled_while_installation_is_disabled(tmp_path, monkeypatch):
    """A settings toggle must not promise updates that cannot be installed."""
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    updater = UpdateManager()
    config_path = tmp_path / ".mentorai" / "config.json"
    original = b'{"auto_updates": false, "user_preference": "offline"}\\n'
    config_path.write_bytes(original)

    assert updater.enable_auto_updates() is False
    assert config_path.read_bytes() == original
    assert "no disponibles" in updater.update_log_path.read_text(encoding="utf-8")


def test_auto_updates_do_not_create_an_enabled_config(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    updater = UpdateManager()
    config_path = tmp_path / ".mentorai" / "config.json"

    assert updater.enable_auto_updates() is False
    assert not config_path.exists()
