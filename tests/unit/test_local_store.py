"""Tests unitarios de la persistencia local cifrada (core.local_store)."""

from __future__ import annotations

import sqlite3

from core.local_store import LocalStore


def _make_store(tmp_path):
    return LocalStore(tmp_path / "profile")


def test_record_query_encrypts_and_rewards(tmp_path):
    store = _make_store(tmp_path)
    before = store.get_progress()
    store.record_query("¿Qué es git?", "Git es un control de versiones.", "Git")
    after = store.get_progress()
    assert after.points == before.points + 10
    assert after.experience == before.experience + 10

    history = store.get_history(1)
    assert history[0].question == "¿Qué es git?"
    assert history[0].answer == "Git es un control de versiones."
    assert history[0].topic == "Git"

    # El texto plano nunca debe aparecer en claro dentro del SQLite.
    with sqlite3.connect(store.db_path) as connection:
        raw = connection.execute(
            "SELECT question_token, answer_token FROM history"
        ).fetchone()
    assert "git" not in (raw[0] + raw[1]).lower()


def test_privacy_summary_counts_every_record(tmp_path):
    store = _make_store(tmp_path)
    for index in range(7):
        store.record_query(f"Pregunta {index}", "Respuesta", "Prueba")
    summary = store.export_privacy_summary()
    assert summary["history_records"] == 7
    assert "AES-256-GCM" in summary["security"]["encryption"]


def test_history_survives_corrupted_ciphertext(tmp_path):
    store = _make_store(tmp_path)
    store.record_query("Pregunta válida", "Respuesta válida", "Prueba")
    with store._connect() as connection:
        connection.execute("UPDATE history SET question_token = 'token-manipulado'")
    history = store.get_history(1)
    assert history[0].question.startswith("[No disponible")
    assert history[0].answer == "Respuesta válida"


def test_set_language_falls_back_to_spanish(tmp_path):
    store = _make_store(tmp_path)
    store.set_language("fr")  # idioma no soportado
    assert store.get_language() == "es"
    store.set_language("ca")
    assert store.get_language() == "ca"


def test_delete_all_wipes_profile_and_history(tmp_path):
    store = _make_store(tmp_path)
    store.record_query("Borrar esto", "Se borrará", "Prueba")
    store.delete_all()
    store.reset_profile()
    assert store.get_progress().points == 0
    assert store.get_history(10) == []


def test_complete_topic_is_idempotent(tmp_path):
    store = _make_store(tmp_path)
    first = store.complete_topic("python")
    second = store.complete_topic("python")
    assert first.topics_completed == 1
    assert second.topics_completed == 1
    assert second.points == first.points
