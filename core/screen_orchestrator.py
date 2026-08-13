import platform
import sys
import os

# Añadir el directorio de módulos nativos al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'native_modules')))

from windows_screen_reader import WindowsScreenReader
from android_screen_reader import AndroidScreenReader

class ScreenOrchestrator:
    def __init__(self):
        self.os_name = platform.system()
        if self.os_name == "Windows":
            self.reader = WindowsScreenReader()
        elif self.os_name == "Linux": # Android suele identificarse como Linux en Python
            # En un entorno real, detectaríamos si es Android específicamente
            self.reader = AndroidScreenReader()
        else:
            self.reader = None

    def capture_and_process(self, mode="accessibility", area=None):
        if not self.reader:
            return "Sistema operativo no soportado para lectura de pantalla."

        if self.os_name == "Windows":
            if mode == "accessibility":
                return self.reader.get_text_at_cursor()
            elif mode == "ocr" and area:
                return self.reader.get_text_from_area(*area)
        
        elif self.os_name == "Linux": # Android simulation
            if mode == "accessibility":
                return self.reader.get_screen_content()
            elif mode == "ocr":
                return self.reader.perform_ocr("path/to/temp/image.png")

        return "Modo de captura no válido."

if __name__ == "__main__":
    orchestrator = ScreenOrchestrator()
    print(f"Sistema detectado: {orchestrator.os_name}")
    print(f"Resultado captura: {orchestrator.capture_and_process()}")
