"""Regresión: el rollback automático debe fallar en cerrado y no borrar nada."""

from __future__ import annotations

from core.updater import UpdateManager


def test_rollback_refuses_and_preserves_directories(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    # Simulamos un directorio de respaldo previo: ni así debe ejecutarse borrado alguno.
    backup = tmp_path / ".mentorai" / "backup_1.0.0"
    backup.mkdir(parents=True)
    (backup / "señal.txt").write_text("respaldo intacto", encoding="utf-8")

    updater = UpdateManager()
    assert updater.rollback_update() is False
    assert (backup / "señal.txt").read_text(encoding="utf-8") == "respaldo intacto"
