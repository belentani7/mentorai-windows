"""Orquestación segura de Professor Mode.

El diseño es deliberadamente de activación explícita: no hay listener global de
teclado, captura periódica ni lectura automática. La UI llama a estos métodos
solo después de una acción visible del usuario.
"""

from __future__ import annotations

import platform
from typing import Any


class ScreenOrchestrator:
    def __init__(self) -> None:
        self.os_name = platform.system()
        self.reader = None
        if self.os_name == "Windows":
            from native_modules.windows_screen_reader import WindowsScreenReader

            self.reader = WindowsScreenReader()

    @property
    def available(self) -> bool:
        return self.reader is not None

    def capabilities(self) -> dict[str, bool]:
        if self.reader is None:
            return {"ui_automation": False, "local_ocr": False}
        return self.reader.capabilities()

    def read_focused_text(self) -> str:
        """Lee solo el control actualmente enfocado tras confirmación del usuario."""
        if self.reader is None:
            return "Professor Mode requiere Windows 10/11 para UI Automation."
        return self.reader.get_text_at_cursor()

    def read_selected_area(self, image: Any, box: tuple[int, int, int, int]) -> str:
        """Procesa un recorte ya seleccionado; no captura la pantalla por sí solo."""
        if self.reader is None:
            return "El OCR de área requiere Windows 10/11."
        return self.reader.get_text_from_area(image, box)

    def capture_and_process(self, mode: str = "accessibility", area: Any = None) -> str:
        """Compatibilidad con el API anterior, manteniendo la activación manual."""
        if mode == "accessibility":
            return self.read_focused_text()
        if mode == "ocr" and area is not None:
            try:
                image, box = area
                return self.read_selected_area(image, box)
            except (TypeError, ValueError):
                return "El OCR necesita una imagen y un rectángulo de recorte válidos."
        return "Modo de lectura no válido."
