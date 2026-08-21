"""Motor local de MentorAI.

Filosofía de este módulo: procesamiento determinista y local, respuestas educativas
explicables y ninguna ejecución de comandos ni conexión de red. El motor recibe
texto que el usuario decide compartir y devuelve datos estructurados para la UI.
"""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


class AssistantEngine:
    """Busca explicaciones en la base de conocimiento empaquetada localmente."""

    MAX_QUERY_LENGTH = 12_000

    _SENSITIVE_PATTERNS = (
        re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
        re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
        re.compile(r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b"),
        re.compile(r"(?i)(?<![a-z0-9])0x[a-f0-9]{39,64}(?![a-z0-9])"),
        re.compile(r"(?i)\b(?:sk|pk|api|token|secret)[-_]?[A-Za-z0-9_\-]{16,}\b"),
        re.compile(r"(?i)\b(?:bearer)\s+[A-Za-z0-9._~+/=-]{16,}\b"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|mariadb)://[^\s]+"),
        re.compile(
            r"-----BEGIN [A-Z ]+ PRIVATE KEY-----.*?-----END [A-Z ]+ PRIVATE KEY-----",
            re.S,
        ),
    )

    def __init__(self, knowledge_base_path: str | Path):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.knowledge_base: dict[str, dict[str, Any]] = self._load_knowledge_base()
        self._normalised_keys = {
            key: self._normalise(key) for key in self.knowledge_base
        }

    @staticmethod
    def _normalise(value: str) -> str:
        value = unicodedata.normalize("NFKD", value)
        value = "".join(char for char in value if not unicodedata.combining(char))
        return re.sub(r"\s+", " ", value.casefold()).strip()

    def _load_knowledge_base(self) -> dict[str, dict[str, Any]]:
        """Carga únicamente JSON con forma de temas; un fichero corrupto no detiene la app."""
        knowledge: dict[str, dict[str, Any]] = {}
        if not self.knowledge_base_path.is_dir():
            return knowledge

        for path in sorted(self.knowledge_base_path.glob("*.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(raw, dict):
                continue
            for key, value in raw.items():
                if isinstance(key, str) and isinstance(value, dict):
                    record = dict(value)
                    record.setdefault("source", path.name)
                    record.setdefault("category", path.stem.replace("_", " ").title())
                    record.setdefault("steps", [])
                    record.setdefault("security_tips", [])
                    knowledge[key] = record
        return knowledge

    def _filter_sensitive_data(self, text: str) -> str:
        """Redacta identificadores comunes antes de conservar o procesar la consulta."""
        filtered = text
        for pattern in self._SENSITIVE_PATTERNS:
            filtered = pattern.sub("[CONFIDENCIAL]", filtered)
        return filtered

    def _find_best_match(self, query: str) -> str | None:
        query_normalised = self._normalise(query)
        if not query_normalised:
            return None

        # Las frases exactas tienen prioridad: «git clone» no debe resolverse como «git».
        exact = [
            (key, len(normalised))
            for key, normalised in self._normalised_keys.items()
            if normalised in query_normalised
        ]
        if exact:
            return max(exact, key=lambda item: item[1])[0]

        query_tokens = set(re.findall(r"[a-z0-9+#.-]+", query_normalised))
        ranked: list[tuple[float, str]] = []
        for key, normalised in self._normalised_keys.items():
            key_tokens = set(re.findall(r"[a-z0-9+#.-]+", normalised))
            overlap = len(query_tokens & key_tokens)
            token_score = overlap / max(len(key_tokens), 1)
            fuzzy_score = difflib.SequenceMatcher(
                None, query_normalised, normalised
            ).ratio()
            # Un término corto mal escrito, como «pyton» o «powershel», debe
            # seguir encontrándose aunque la pregunta contenga palabras extra.
            token_fuzzy = max(
                (
                    difflib.SequenceMatcher(None, token, key_token).ratio()
                    for token in query_tokens
                    for key_token in key_tokens
                ),
                default=0.0,
            )
            score = token_score * 0.60 + fuzzy_score * 0.15 + token_fuzzy * 0.25
            if overlap or fuzzy_score >= 0.62 or token_fuzzy >= 0.78:
                ranked.append((score, key))
        if not ranked:
            return None
        score, key = max(ranked)
        return key if score >= 0.30 else None

    def search_topics(self, query: str = "") -> list[dict[str, str]]:
        """Devuelve temas para la navegación, sin exponer el contenido completo de la KB."""
        query_normalised = self._normalise(query)
        topics = []
        for key, data in self.knowledge_base.items():
            searchable = self._normalise(
                f"{key} {data.get('category', '')} {data.get('explanation', '')}"
            )
            if not query_normalised or query_normalised in searchable:
                topics.append(
                    {
                        "key": key,
                        "category": str(data.get("category", "General")),
                        "label": key.replace("_", " ").title(),
                    }
                )
        return sorted(topics, key=lambda topic: (topic["category"], topic["label"]))

    def process_query(
        self, extracted_text: str, language: str = "es"
    ) -> dict[str, Any]:
        """Procesa una consulta sin ejecutar código, órdenes ni acciones externas."""
        if not isinstance(extracted_text, str):
            return {"status": "error", "message": "La consulta debe ser texto."}
        if not extracted_text.strip():
            return {
                "status": "error",
                "message": "No se proporcionó texto para procesar.",
            }
        if len(extracted_text) > self.MAX_QUERY_LENGTH:
            return {
                "status": "error",
                "message": f"La consulta supera el límite seguro de {self.MAX_QUERY_LENGTH} caracteres.",
            }

        clean_text = self._filter_sensitive_data(extracted_text.strip())
        matched_key = self._find_best_match(clean_text)
        fallback = {
            "es": "Todavía no tengo una explicación específica para esa consulta. Prueba con un tema de la lista o con términos como CMD, PowerShell, Python, Git, Docker, Android o seguridad.",
            "en": "I do not have a specific explanation for that query yet. Try a topic from the list or terms such as CMD, PowerShell, Python, Git, Docker, Android, or security.",
            "pt": "Ainda não tenho uma explicação específica para essa pergunta. Tente um tema da lista ou termos como CMD, PowerShell, Python, Git, Docker, Android ou segurança.",
            "ca": "Encara no tinc una explicació específica per a aquesta consulta. Prova un tema de la llista o termes com CMD, PowerShell, Python, Git, Docker, Android o seguretat.",
        }.get(language, "es")

        response: dict[str, Any] = {
            "status": "success",
            "original_query": clean_text,
            "language": language,
            "matched_term": matched_key,
            "topic": "General",
            "explanation": fallback,
            "steps": [],
            "security_tips": [
                "MentorAI no ejecuta comandos automáticamente; explica lo que podrías hacer y tú decides.",
                "No compartas contraseñas, claves privadas, códigos de recuperación ni tokens.",
            ],
            "safety_notice": "Respuesta generada exclusivamente desde la base de conocimiento local.",
        }

        if matched_key is not None:
            data = self.knowledge_base[matched_key]
            response.update(
                {
                    "explanation": str(data.get("explanation", fallback)),
                    "steps": [
                        str(step) for step in data.get("steps", []) if step is not None
                    ],
                    "security_tips": [
                        str(tip)
                        for tip in data.get("security_tips", [])
                        if tip is not None
                    ],
                    "topic": str(data.get("category", "General")),
                }
            )
        return response


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    engine = AssistantEngine(root / "knowledge_base")
    print(engine.process_query("¿Cómo funciona git clone?"))
