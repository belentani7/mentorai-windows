# -*- mode: python ; coding: utf-8 -*-
"""Build reproducible de MentorAI para Windows x64."""

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project_root = Path(SPEC).resolve().parent

hiddenimports = []
hiddenimports += collect_submodules("PyQt5")
for optional_module in ("pytesseract", "PIL", "uiautomation"):
    try:
        hiddenimports += collect_submodules(optional_module)
    except Exception:
        # El build sigue siendo válido sin los extras opcionales; la UI mostrará
        # una explicación en lugar de fallar al arrancar.
        pass

# La base de conocimiento debe estar dentro del bundle para que la aplicación
# no dependa del directorio de trabajo del usuario.
datas = [
    (str(project_root / "knowledge_base"), "knowledge_base"),
]

analysis = Analysis(
    [str(project_root / "ui" / "mentorai_windows_ui.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="MentorAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)
