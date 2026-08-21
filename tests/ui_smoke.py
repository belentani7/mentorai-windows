"""Smoke test headless de la ventana PyQt5 de MentorAI."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt5.QtWidgets import QApplication

from ui.mentorai_windows_ui import MentorAIWindow


def main() -> int:
    app = QApplication.instance() or QApplication([])
    window = MentorAIWindow()
    assert window.windowTitle().startswith("MentorAI")
    assert window.topics_list.count() >= 35
    assert window.screen_orchestrator is not None
    window.close()
    app.processEvents()
    print("UI SMOKE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
