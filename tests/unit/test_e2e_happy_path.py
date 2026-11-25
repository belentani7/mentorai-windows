"""Camino feliz extremo a extremo: consultar → aprender → registrar → borrar.

Ejercita el motor, el almacén cifrado y el borrado de datos en un único flujo,
como lo haría un usuario real de la aplicación.
"""

from __future__ import annotations

from pathlib import Path

from core.assistant_engine import AssistantEngine
from core.local_store import LocalStore

ROOT = Path(__file__).resolve().parents[2]


def test_happy_path_question_to_erasure(tmp_path):
    engine = AssistantEngine(ROOT / "knowledge_base")
    store = LocalStore(tmp_path / "profile")

    # 1) El usuario pregunta por rutas de aprendizaje
    paths = engine.get_learning_paths()
    assert {path["id"] for path in paths} == {"windows", "python", "git", "security"}

    # 2) Hace una consulta real y obtiene una explicación útil
    answer = engine.process_query("¿Cómo clono un repositorio con git clone?")
    assert answer["status"] == "success"
    assert answer["matched_term"] == "git clone"
    assert answer["steps"], "La respuesta debe incluir pasos guiados"

    # 3) El historial queda cifrado pero recuperable
    store.record_query(
        "¿Cómo clono un repositorio con git clone?",
        answer["explanation"],
        answer["topic"],
    )
    history = store.get_history(1)
    assert history[0].question.startswith("¿Cómo clono")
    assert store.get_progress().points == 10

    # 4) El informe de privacidad refleja el registro
    summary = store.export_privacy_summary()
    assert summary["history_records"] == 1

    # 5) El usuario borra sus datos: nada debe sobrevivir
    store.delete_all()
    store.reset_profile()
    assert store.get_history(10) == []
    assert store.get_progress().points == 0
    fresh = store.export_privacy_summary()
    assert fresh["history_records"] == 0
