#!/usr/bin/env python3
"""Offline learning-flow checks, NOT a usability study with children.

This script verifies educational answers and typo handling from the packaged
knowledge base. Visual design, accessibility and comprehension by real people
must be evaluated separately on the target Windows UI.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.assistant_engine import AssistantEngine


def main() -> int:
    engine = AssistantEngine(ROOT / "knowledge_base")
    assert len(engine.knowledge_base) >= 35, "Base de conocimiento no disponible"

    checked = 0
    for query, topic in (
        ("¿Qué es cd?", "cd"),
        ("¿Qué es Python?", "python"),
        ("¿Qué es Android?", "android"),
        ("powershel", "powershell"),
        ("pyton", "python"),
        ("andorid", "android"),
    ):
        answer = engine.process_query(query)
        assert answer["matched_term"] == topic, (query, answer["matched_term"])
        assert answer["explanation"].strip(), query
        assert answer["steps"], f"Faltan pasos para {query}"
        assert answer["security_tips"], f"Faltan consejos de seguridad para {query}"
        checked += 1

    # Measure actual coverage; a generic fallback is not a successful lesson.
    unsupported = ("¿Cómo cambio de carpeta?", "¿Cómo instalo un programa?")
    gaps = [q for q in unsupported if engine.process_query(q)["matched_term"] is None]
    print(f"PASS: {checked} consultas y errores tipográficos con tema, pasos y seguridad")
    print(f"Cobertura pendiente de lenguaje natural: {len(gaps)}/{len(unsupported)}")
    for query in gaps:
        print(f"  SIN TEMA: {query}")
    print("No se ha probado interfaz, accesibilidad ni comprensión de menores reales.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
