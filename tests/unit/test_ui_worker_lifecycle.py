"""Offline regression checks for the Qt worker signal contract.

These tests execute the *actual worker class AST* with a tiny synchronous
QThread signal double, without importing PyQt5 or accessing a user's desktop.
Real Windows/Qt UI tests are still required before release.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UI_FILE = ROOT / "ui" / "mentorai_windows_ui.py"


class BoundSignal:
    def __init__(self):
        self.handlers = []

    def connect(self, callback):
        self.handlers.append(callback)

    def emit(self, *args):
        for callback in list(self.handlers):
            callback(*args)


class Signal:
    def __set_name__(self, owner, name):
        self.name = "_signal_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = BoundSignal()
        return instance.__dict__[self.name]


class FakeQThread:
    finished = Signal()

    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        try:
            self.run()
        finally:
            self.running = False
            self.finished.emit()

    def isRunning(self):
        return self.running


def load_workers():
    tree = ast.parse(UI_FILE.read_text(encoding="utf-8"))
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name in {"QueryWorker", "ScreenReadWorker"}
    ]
    assert len(nodes) == 2
    namespace = {
        "QThread": FakeQThread,
        "pyqtSignal": lambda *args: Signal(),
        "AssistantEngine": object,
        "ScreenOrchestrator": object,
        "Any": object,
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(UI_FILE), "exec"), namespace)
    return namespace


class WorkerLifecycleTests(unittest.TestCase):
    def test_query_result_before_thread_finished(self):
        cls = load_workers()["QueryWorker"]
        engine = type("Engine", (), {"process_query": lambda self, q, lang: {"q": q, "lang": lang}})()
        worker = cls(engine, "consulta", "es")
        events = []
        worker.result_ready.connect(lambda value: events.append(("result", value)))
        worker.finished.connect(lambda: events.append(("thread_finished", None)))
        worker.start()
        self.assertEqual(events, [
            ("result", {"q": "consulta", "lang": "es"}),
            ("thread_finished", None),
        ])

    def test_query_exception_emits_failure_then_thread_finished(self):
        cls = load_workers()["QueryWorker"]
        def fail(*args):
            raise ValueError("offline error")
        worker = cls(type("Engine", (), {"process_query": fail})(), "q", "es")
        events = []
        worker.failed.connect(lambda message: events.append(("failed", message)))
        worker.finished.connect(lambda: events.append(("thread_finished", None)))
        worker.start()
        self.assertEqual(events, [("failed", "offline error"), ("thread_finished", None)])

    def test_screen_worker_result_and_failure(self):
        cls = load_workers()["ScreenReadWorker"]
        orchestrator = type("OCR", (), {"read_focused_text": lambda self: "local"})()
        worker = cls(orchestrator, "focused")
        events = []
        worker.result_ready.connect(events.append)
        worker.finished.connect(lambda: events.append("thread_finished"))
        worker.start()
        self.assertEqual(events, ["local", "thread_finished"])

    def test_ui_wires_real_thread_finish_and_keyboard_access(self):
        source = UI_FILE.read_text(encoding="utf-8")
        self.assertEqual(source.count(".result_ready.connect("), 3)
        self.assertEqual(source.count(".finished.connect(self._release_"), 3)
        self.assertIn("self.topics_list.itemActivated.connect(self._topic_selected)", source)
        self.assertIn("self.input_field.setText(self.last_question)", source)
        self.assertIn("event.ignore()", source)
        self.assertNotIn("self.worker.quit()", source)
        self.assertNotIn("self.screen_worker.quit()", source)


if __name__ == "__main__":
    unittest.main()
