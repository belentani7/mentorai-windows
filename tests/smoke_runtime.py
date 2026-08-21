"""Smoke test ejecutable sin entorno gráfico para la base local de MentorAI."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.assistant_engine import AssistantEngine
from core.local_store import LocalStore
from core.security_manager import SecurityError, SecurityManager


def main() -> int:
    engine = AssistantEngine(ROOT / "knowledge_base")
    assert len(engine.knowledge_base) >= 35
    answer = engine.process_query("¿Qué es powershel?")
    assert answer["status"] == "success"
    assert answer["matched_term"] == "powershell"
    sensitive = engine.process_query(
        "Mi email es persona@example.com y mi clave es sk_test_1234567890123456"
    )
    assert "persona@example.com" not in sensitive["original_query"]
    assert "sk_test_1234567890123456" not in sensitive["original_query"]

    with tempfile.TemporaryDirectory(prefix="mentorai-smoke-") as folder:
        store = LocalStore(folder)
        before = store.get_progress()
        store.record_query("Pregunta local", "Respuesta local", "Prueba")
        after = store.get_progress()
        assert after.points == before.points + 10
        assert store.get_history(1)[0].question == "Pregunta local"

        security = SecurityManager(data_dir=Path(folder) / "security")
        token = security.encrypt_data("dato confidencial", "smoke")
        assert security.decrypt_data(token, "smoke") == "dato confidencial"
        try:
            security.decrypt_data(token, "wrong-aad")
        except SecurityError:
            pass
        else:
            raise AssertionError("El token manipulado debe fallar")

        store.delete_all()
        store.reset_profile()
        assert store.get_progress().points == 0
        assert store.get_history(1) == []

    print("SMOKE RUNTIME PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
