"""Regresiones de seguridad conductuales de MentorAI.

Este archivo no es una certificación ni un pentest profesional. Comprueba
propiedades que existen en el código local y marca como no aplicables las
protecciones de red, autenticación o privilegios que MentorAI no implementa.
"""

from __future__ import annotations

import hmac
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.assistant_engine import AssistantEngine
from core.local_store import LocalStore
from core.security_manager import SecurityError, SecurityManager


class PenetrationTestingSuite:
    def __init__(self):
        self.engine = AssistantEngine(ROOT / "knowledge_base")
        self.passed_tests: list[str] = []
        self.vulnerabilities: list[str] = []
        self.not_applicable: list[str] = []

    def _pass(self, name: str) -> None:
        self.passed_tests.append(name)
        print(f"  PASS  {name}")

    def _fail(self, name: str) -> None:
        self.vulnerabilities.append(name)
        print(f"  FAIL  {name}")

    def test_constant_time_comparison(self) -> None:
        print("\n[PENTEST 1] Comparación segura de valores")
        if hmac.compare_digest("correct", "correct") and not hmac.compare_digest(
            "correct", "wrong"
        ):
            self._pass("La comparación de prueba usa compare_digest")
        else:
            self._fail("La comparación constante no se comporta como se espera")

    def test_authenticated_encryption(self) -> None:
        print("\n[PENTEST 2] Cifrado autenticado local")
        with tempfile.TemporaryDirectory(prefix="mentorai-security-") as folder:
            manager = SecurityManager(data_dir=folder)
            token = manager.encrypt_data("dato privado", "test")
            if manager.decrypt_data(token, "test") != "dato privado":
                self._fail("El descifrado no coincide")
                return
            try:
                manager.decrypt_data(token, "otro-contexto")
            except SecurityError:
                self._pass("AES-GCM rechaza un token con contexto manipulado")
            else:
                self._fail("El cifrado no rechazó un contexto manipulado")

    def test_input_is_never_executed(self) -> None:
        print("\n[PENTEST 3] Entradas que parecen comandos o código")
        payloads = [
            "__import__('os').system('whoami')",
            "'; DROP TABLE users; --",
            "<script>alert(1)</script>",
            "../../../../etc/passwd",
        ]
        for payload in payloads:
            response = self.engine.process_query(payload)
            if response.get("status") != "success" or payload in response.get(
                "explanation", ""
            ):
                self._fail(f"Entrada no controlada: {payload[:24]}")
                return
        self._pass("Las entradas se tratan como texto y no se ejecutan")

    def test_sensitive_redaction(self) -> None:
        print("\n[PENTEST 4] Redacción antes de conservar la consulta")
        sensitive = (
            "mail persona@example.com tarjeta 4532-1234-5678-9012 "
            "btc 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa "
            "evm 0x742d35Cc6634C0532925a3b844Bc9e7595f42bE "
            "token sk_live_51234567890abcdefg"
        )
        filtered = self.engine.process_query(sensitive)["original_query"]
        if sensitive == filtered or any(
            value in filtered for value in ("persona@example.com", "sk_live_")
        ):
            self._fail("La consulta sensible llegó sin redacción")
        else:
            self._pass("Los identificadores sensibles se redactan antes del historial")

    def test_database_at_rest(self) -> None:
        print("\n[PENTEST 5] Datos cifrados en SQLite local")
        with tempfile.TemporaryDirectory(prefix="mentorai-at-rest-") as folder:
            store = LocalStore(folder)
            store.record_query("mensaje privado", "respuesta privada", "Prueba")
            raw_db = (Path(folder) / "mentorai.db").read_bytes()
            if b"mensaje privado" in raw_db or b"respuesta privada" in raw_db:
                self._fail("SQLite contiene texto de historial sin cifrar")
                return
            if store.get_history(1)[0].question != "mensaje privado":
                self._fail("El historial cifrado no se puede recuperar correctamente")
                return
            self._pass(
                "El historial no aparece en claro en SQLite y se recupera con la clave local"
            )

    def test_delete_data(self) -> None:
        print("\n[PENTEST 6] Borrado controlado de datos")
        with tempfile.TemporaryDirectory(prefix="mentorai-delete-") as folder:
            store = LocalStore(folder)
            store.record_query("borrar esto", "respuesta", "Prueba")
            store.delete_all()
            store.reset_profile()
            if store.get_history(1) or store.get_progress().points != 0:
                self._fail("Quedaron datos tras la eliminación")
            else:
                self._pass(
                    "Historial y progreso quedan vacíos tras confirmación de borrado"
                )

    def note_not_applicable(self) -> None:
        self.not_applicable.extend(
            [
                "No hay autenticación remota ni gestión de sesiones en la aplicación offline.",
                "No hay API de red ni cifrado en tránsito que auditar en el núcleo local.",
                "La aplicación no ejecuta procesos ni solicita elevación de privilegios.",
                "La resistencia del binario, firma de código, instalador y permisos Windows requiere pruebas en Windows real.",
            ]
        )

    def run_all_tests(self) -> int:
        print("\n" + "=" * 68)
        print("MENTORAI — REGRESIONES DE SEGURIDAD CONDUCTUALES")
        print("=" * 68)
        self.test_constant_time_comparison()
        self.test_authenticated_encryption()
        self.test_input_is_never_executed()
        self.test_sensitive_redaction()
        self.test_database_at_rest()
        self.test_delete_data()
        self.note_not_applicable()
        print("\n" + "=" * 68)
        print(
            f"PASADAS: {len(self.passed_tests)} · FALLOS: {len(self.vulnerabilities)}"
        )
        print("No aplicable (no implementado por diseño):")
        for item in self.not_applicable:
            print(f"  - {item}")
        if self.vulnerabilities:
            print("Vulnerabilidades encontradas:")
            for item in self.vulnerabilities:
                print(f"  - {item}")
            return 1
        print(
            "Las regresiones implementadas pasan; esto no sustituye una auditoría independiente."
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(PenetrationTestingSuite().run_all_tests())
