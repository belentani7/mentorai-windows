"""Atajo global mínimo para Professor Mode.

Solo registra Ctrl+Shift+M mediante RegisterHotKey: Windows notifica esa
combinación exacta y el módulo no instala un teclado global ni captura otras
pulsaciones.
"""

from __future__ import annotations

import ctypes
import platform
from ctypes import wintypes

from PyQt5.QtCore import QAbstractNativeEventFilter, QObject, pyqtSignal


class WindowsProfessorHotkey(QObject, QAbstractNativeEventFilter):
    activated = pyqtSignal()
    HOTKEY_ID = 0x4D4152  # identificador interno fijo: «MAR»
    WM_HOTKEY = 0x0312
    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        QAbstractNativeEventFilter.__init__(self)
        self.registered = False

    def register(self) -> bool:
        if platform.system() != "Windows":
            return False
        user32 = ctypes.windll.user32
        self.registered = bool(
            user32.RegisterHotKey(
                None, self.HOTKEY_ID, self.MOD_CONTROL | self.MOD_SHIFT, ord("M")
            )
        )
        return self.registered

    def unregister(self) -> None:
        if self.registered and platform.system() == "Windows":
            ctypes.windll.user32.UnregisterHotKey(None, self.HOTKEY_ID)
        self.registered = False

    def nativeEventFilter(self, eventType, message):  # noqa: N802
        if platform.system() != "Windows":
            return False, 0
        try:
            pointer = int(message)
            wparam = ctypes.cast(pointer, ctypes.POINTER(wintypes.MSG)).contents.wParam
            if wparam == self.HOTKEY_ID:
                self.activated.emit()
                return True, 0
        except (TypeError, ValueError, OSError):
            pass
        return False, 0
