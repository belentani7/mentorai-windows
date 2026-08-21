"""Adaptador Windows para lectura de accesibilidad y OCR local.

El módulo solo lee cuando la capa de UI lo solicita. Nunca hace clic, escribe,
ejecuta procesos ni envía capturas a una red.
"""

from __future__ import annotations

import platform
from typing import Any


class WindowsScreenReader:
    """Lectura defensiva de controles accesibles y de imágenes seleccionadas."""

    def __init__(self) -> None:
        self.os_type = platform.system()

    def get_text_at_cursor(self) -> str:
        if self.os_type != "Windows":
            return "La lectura de accesibilidad solo está disponible en Windows."
        try:
            import uiautomation as auto
        except ImportError:
            return "Falta el componente opcional UI Automation (uiautomation)."

        try:
            control = auto.GetFocusedControl()
            if control is None:
                return "No se encontró un control accesible enfocado."
            control_type = str(getattr(control, "ControlTypeName", ""))
            # No intentamos leer controles marcados como contraseña.
            if (
                "password" in control_type.casefold()
                or "password" in str(getattr(control, "Name", "")).casefold()
            ):
                return "Por privacidad, MentorAI no lee controles de contraseña."

            parts: list[str] = []
            name = str(getattr(control, "Name", "") or "").strip()
            if name:
                parts.append(name)
            try:
                value_pattern = control.GetValuePattern()
                value = str(getattr(value_pattern, "Value", "") or "").strip()
                if value and value != name:
                    parts.append(value)
            except Exception:
                pass
            try:
                help_text = str(getattr(control, "HelpText", "") or "").strip()
                if help_text and help_text not in parts:
                    parts.append(help_text)
            except Exception:
                pass
            return (
                "\n".join(dict.fromkeys(parts))
                or "El control enfocado no expone texto accesible."
            )
        except Exception as exc:
            return f"No se pudo leer el control accesible de forma segura: {exc}"

    def get_text_from_area(
        self,
        image: Any,
        box: tuple[int, int, int, int],
        language: str = "spa+eng+por+cat",
    ) -> str:
        """Ejecuta OCR solo sobre el recorte seleccionado, si el proveedor está instalado."""
        if self.os_type != "Windows":
            return "El OCR de pantalla solo está disponible en Windows."
        try:
            if hasattr(image, "bits") and hasattr(image, "width"):
                # QImage.Format_RGBA8888 llega desde la UI; se convierte solo en memoria.
                from PIL import Image

                from PyQt5.QtGui import QImage

                converted = image.convertToFormat(QImage.Format_RGBA8888)
                pointer = converted.bits()
                pointer.setsize(converted.byteCount())
                source = Image.frombuffer(
                    "RGBA",
                    (converted.width(), converted.height()),
                    bytes(pointer),
                    "raw",
                    "RGBA",
                    converted.bytesPerLine(),
                    1,
                )
                crop = source.crop(box)
            else:
                crop = image.crop(box)
        except Exception as exc:
            return f"No se pudo preparar el área seleccionada: {exc}"
        try:
            import pytesseract
        except ImportError:
            return (
                "OCR local no disponible todavía. Instala Tesseract OCR y el paquete "
                "pytesseract; la imagen seleccionada no se ha enviado ni guardado."
            )
        try:
            text = pytesseract.image_to_string(crop, lang=language).strip()
        except Exception as exc:
            return f"OCR local no pudo procesar el área: {exc}"
        return text or "No se detectó texto en el área seleccionada."

    def capabilities(self) -> dict[str, bool]:
        capabilities = {"ui_automation": False, "local_ocr": False}
        if self.os_type != "Windows":
            return capabilities
        try:
            import uiautomation  # noqa: F401

            capabilities["ui_automation"] = True
        except ImportError:
            pass
        try:
            import pytesseract  # noqa: F401

            capabilities["local_ocr"] = True
        except ImportError:
            pass
        return capabilities
