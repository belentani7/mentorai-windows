from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
errors: list[str] = []

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

for path in ROOT.rglob("*.py"):
    if any(part in {".git", "__pycache__"} for part in path.parts):
        continue
    try:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    except Exception as exc:
        errors.append(f"invalid Python {path.relative_to(ROOT)}: {exc}")

for path in ROOT.rglob("*"):
    if not path.is_file() or any(part in {".git", "__pycache__"} for part in path.parts):
        continue
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
