from __future__ import annotations

import json
import os
import pathlib
import sys
from pathlib import Path

ROOT = pathlib.Path(__file__).resolve().parents[1]
errors: list[str] = []

# Directorios generados o de terceros que nunca son "fuente" del repositorio.
IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".env",
    "node_modules",
    "dist",
    "build",
    "out",
    ".next",
    ".nuxt",
    "coverage",
    "htmlcov",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".turbo",
    "site-packages",
    ".eggs",
}

required = [
    ROOT / "cli" / "mentorai_cli.py",
    ROOT / "ui" / "mentorai_windows_ui.py",
    ROOT / "core" / "assistant_engine.py",
    ROOT / "knowledge_base",
    ROOT / "tests",
    ROOT / "mentorai_windows.spec",
    ROOT / ".github" / "workflows" / "windows-build.yml",
]
for path in required:
    if not path.exists():
        errors.append(f"missing: {path.relative_to(ROOT)}")

for path in sorted((ROOT / "knowledge_base").glob("*.json")):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path.name}: {exc}")


def iter_source_files():
    """Recorre el árbol sin descender en directorios generados (rápido y sin ruido)."""
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for filename in filenames:
            yield Path(dirpath) / filename


for path in iter_source_files():
    if path.suffix != ".py":
        continue
    try:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    except Exception as exc:
        errors.append(f"invalid Python {path.relative_to(ROOT)}: {exc}")

for path in iter_source_files():
    try:
        with path.open("rb") as handle:
            signature = handle.read(2)
        if signature == b"MZ" and path.suffix.lower() not in {".ico"}:
            errors.append(f"unexpected Windows binary in source tree: {path.relative_to(ROOT)}")
        if signature == b"EL" and path.suffix.lower() not in {".json"}:
            errors.append(f"unexpected ELF binary in source tree: {path.relative_to(ROOT)}")
    except OSError as exc:
        errors.append(f"cannot read {path}: {exc}")

if errors:
    print("VALIDATION FAILED")
    print("\n".join(errors))
    sys.exit(1)

print("VALIDATION PASSED")
print(f"root={ROOT}")
print(f"knowledge_files={len(list((ROOT / 'knowledge_base').glob('*.json')))}")
print("python_sources=ok")
print("required_paths=ok")
print("source_binary_scan=ok")
