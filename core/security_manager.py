"""Protección de datos locales de MentorAI.

Este módulo no envía datos a Internet. Usa AES-256-GCM para confidencialidad e
integridad. En Windows, la clave maestra se protege con DPAPI para que solo la
cuenta de usuario que creó la instalación pueda recuperarla.
"""

from __future__ import annotations

import base64
import json
import os
import secrets
import shutil
import sys
from pathlib import Path
from typing import Iterable

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:  # pragma: no cover - dependency is pinned for Windows builds
    AESGCM = None  # type: ignore[assignment,misc]


class SecurityError(RuntimeError):
    """Error controlado de protección o descifrado local."""


class SecurityManager:
    """Gestiona la clave local y el cifrado autenticado de pequeños documentos."""

    KEY_SIZE = 32
    NONCE_SIZE = 12
    KEY_FILE = "master.key"
    KEY_HEADER = b"MENTORAI-DPAPI-1\0"

    def __init__(self, device_id: str = "mentorai", data_dir: str | Path | None = None):
        self.device_id = device_id
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".mentorai"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.key_path = self.data_dir / self.KEY_FILE
        self._key = self._load_or_create_key()

    @property
    def uses_os_protected_key(self) -> bool:
        return sys.platform == "win32"

    def _load_or_create_key(self) -> bytes:
        if self.key_path.exists():
            try:
                stored = self.key_path.read_bytes()
                if stored.startswith(self.KEY_HEADER):
                    return self._unprotect_with_dpapi(stored[len(self.KEY_HEADER) :])
                if len(stored) == self.KEY_SIZE and sys.platform != "win32":
                    return stored
                raise SecurityError(
                    "La clave local no tiene un formato protegido válido."
                )
            except OSError as exc:
                raise SecurityError(f"No se pudo leer la clave local: {exc}") from exc

        key = secrets.token_bytes(self.KEY_SIZE)
        if sys.platform == "win32":
            payload = self.KEY_HEADER + self._protect_with_dpapi(key)
        else:
            # El fallback existe para desarrollo/test multiplataforma. En Windows se usa DPAPI.
            payload = key
        try:
            self.key_path.write_bytes(payload)
            try:
                os.chmod(self.key_path, 0o600)
            except OSError:
                pass
        except OSError as exc:
            raise SecurityError(f"No se pudo guardar la clave local: {exc}") from exc
        return key

    @staticmethod
    def _protect_with_dpapi(data: bytes) -> bytes:
        if sys.platform != "win32":
            return data
        import ctypes
        from ctypes import wintypes

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [
                ("cbData", wintypes.DWORD),
                ("pbData", ctypes.POINTER(ctypes.c_byte)),
            ]

        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        source = ctypes.create_string_buffer(data)
        input_blob = DATA_BLOB(
            len(data), ctypes.cast(source, ctypes.POINTER(ctypes.c_byte))
        )
        output_blob = DATA_BLOB()
        if not crypt32.CryptProtectData(
            ctypes.byref(input_blob),
            "MentorAI key",
            None,
            None,
            None,
            0,
            ctypes.byref(output_blob),
        ):
            raise SecurityError("Windows DPAPI no pudo proteger la clave local.")
        try:
            return ctypes.string_at(output_blob.pbData, output_blob.cbData)
        finally:
            kernel32.LocalFree(output_blob.pbData)

    @staticmethod
    def _unprotect_with_dpapi(data: bytes) -> bytes:
        if sys.platform != "win32":
            return data
        import ctypes
        from ctypes import wintypes

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [
                ("cbData", wintypes.DWORD),
                ("pbData", ctypes.POINTER(ctypes.c_byte)),
            ]

        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        source = ctypes.create_string_buffer(data)
        input_blob = DATA_BLOB(
            len(data), ctypes.cast(source, ctypes.POINTER(ctypes.c_byte))
        )
        output_blob = DATA_BLOB()
        if not crypt32.CryptUnprotectData(
            ctypes.byref(input_blob),
            None,
            None,
            None,
            None,
            0,
            ctypes.byref(output_blob),
        ):
            raise SecurityError(
                "Windows DPAPI no pudo recuperar la clave local; puede pertenecer a otro usuario."
            )
        try:
            key = ctypes.string_at(output_blob.pbData, output_blob.cbData)
        finally:
            kernel32.LocalFree(output_blob.pbData)
        if len(key) != SecurityManager.KEY_SIZE:
            raise SecurityError("La clave recuperada no tiene 256 bits.")
        return key

    def encrypt_data(self, data: str, associated_data: str = "") -> str:
        """Cifra texto y devuelve un token base64url con nonce y etiqueta GCM."""
        if AESGCM is None:
            raise SecurityError(
                "Falta la dependencia cryptography; instala requirements-windows.txt."
            )
        if not isinstance(data, str):
            raise TypeError("Solo se puede cifrar texto UTF-8.")
        nonce = secrets.token_bytes(self.NONCE_SIZE)
        aad = associated_data.encode("utf-8")
        ciphertext = AESGCM(self._key).encrypt(nonce, data.encode("utf-8"), aad)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")

    def decrypt_data(self, encrypted_str: str, associated_data: str = "") -> str:
        """Verifica y descifra un token; cualquier manipulación produce SecurityError."""
        if AESGCM is None:
            raise SecurityError(
                "Falta la dependencia cryptography; instala requirements-windows.txt."
            )
        try:
            payload = base64.urlsafe_b64decode(encrypted_str.encode("ascii"))
            nonce, ciphertext = payload[: self.NONCE_SIZE], payload[self.NONCE_SIZE :]
            if len(nonce) != self.NONCE_SIZE or len(ciphertext) < 16:
                raise ValueError("token incompleto")
            plain = AESGCM(self._key).decrypt(
                nonce,
                ciphertext,
                associated_data.encode("utf-8"),
            )
            return plain.decode("utf-8")
        except Exception as exc:
            raise SecurityError(
                "No se pudo verificar o descifrar el contenido local."
            ) from exc

    def encrypt_json(self, value: object, associated_data: str = "") -> str:
        return self.encrypt_data(
            json.dumps(value, ensure_ascii=False, separators=(",", ":")),
            associated_data,
        )

    def decrypt_json(self, token: str, associated_data: str = "") -> object:
        return json.loads(self.decrypt_data(token, associated_data))

    def generate_privacy_report(self) -> dict[str, object]:
        return {
            "processing": "Local-first; este módulo no realiza conexiones de red.",
            "encryption": "AES-256-GCM con detección de manipulación.",
            "key_protection": (
                "Windows DPAPI ligado a la cuenta local"
                if self.uses_os_protected_key
                else "Clave de desarrollo local con permisos restringidos; Windows usa DPAPI."
            ),
            "screen_capture": "Solo se procesa cuando el usuario activa explícitamente Professor Mode.",
            "third_party_sharing": "Ninguno desde el núcleo local.",
            "user_controls": [
                "Consultar datos locales",
                "Borrar datos locales",
                "No iniciar acciones del sistema automáticamente",
            ],
        }

    @staticmethod
    def _best_effort_delete(path: Path) -> None:
        if not path.exists():
            return
        if path.is_file():
            try:
                size = path.stat().st_size
                with path.open("r+b") as handle:
                    handle.write(b"\0" * min(size, 1024 * 1024))
                    handle.flush()
                    os.fsync(handle.fileno())
            except OSError:
                pass
            path.unlink(missing_ok=True)
        elif path.is_dir():
            shutil.rmtree(path, ignore_errors=False)

    def wipe_all_data(self, paths: Iterable[str | Path] | None = None) -> str:
        """Elimina datos locales seleccionados; el usuario debe confirmar la acción en la UI."""
        targets = (
            [Path(path) for path in paths] if paths is not None else [self.data_dir]
        )
        for target in targets:
            self._best_effort_delete(target)
        return "Los datos locales seleccionados se han eliminado."


if __name__ == "__main__":
    manager = SecurityManager(data_dir=Path.home() / ".mentorai")
    token = manager.encrypt_data("prueba local")
    print(manager.decrypt_data(token))
