"""Executable language-tolerant matching tests — real offline engine."""
import tempfile
import unittest
import json
from pathlib import Path
from core.assistant_engine import AssistantEngine


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = Path(self.temp.name)
        (path / "topics.json").write_text(json.dumps({
            "git": {"explanation": "Control de versiones", "category": "Herramientas"},
            "digital": {"explanation": "Alfabetización digital", "category": "Formación"},
            "git clone": {"explanation": "Descarga repositorios", "category": "Herramientas"},
            "powershell": {"explanation": "Terminal Windows", "category": "Herramientas"},
        }), encoding="utf-8")
        self.engine = AssistantEngine(path)

    def test_full_word_git_does_not_match_inside_digital(self):
        self.assertEqual(self.engine.process_query("Curso digital")["matched_term"], "digital")

    def test_git_keyword_still_matches_when_isolated(self):
        self.assertEqual(self.engine.process_query("Explícame git")["matched_term"], "git")

    def test_longer_phrase_beats_shorter_exact_keyword(self):
        self.assertEqual(self.engine.process_query("¿Cómo usar git clone?")["matched_term"], "git clone")

    def test_typo_tolerant_matching_remains(self):
        self.assertEqual(self.engine.process_query("Como funciona powershel")["matched_term"], "powershell")

    def test_no_substring_match_from_words_only_containing_keyword(self):
        self.assertNotEqual(self.engine.process_query("digitalizador")["matched_term"], "git")

    def test_never_runs_commands_or_uploads_query(self):
        self.assertEqual(self.engine.process_query("Explícame git")["status"], "success")
        self.assertEqual(self.engine.process_query("A"*12001)["status"], "error")


if __name__ == "__main__":
    unittest.main()
