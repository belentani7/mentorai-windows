import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.assistant_engine import AssistantEngine

def test_engine():
    kb_path = ROOT / 'knowledge_base'
    engine = AssistantEngine(kb_path)

    # Test case 1: Windows CMD
    print("Testing 'cd' command:")
    result = engine.process_query("¿Cómo uso el comando cd?")
    print(f"Explanation: {result['explanation']}")
    
    # Test case 2: Crypto Security
    print("\nTesting 'Binance' security:")
    result = engine.process_query("Quiero entrar en Binance")
    print(f"Security Tips: {result['security_tips']}")

    # Test case 3: Sensitive data filtering
    print("\nTesting sensitive data filtering:")
    sensitive_text = "Mi clave es 1234-5678-9012-3456 y mi correo es test@example.com"
    result = engine.process_query(sensitive_text)
    print(f"Filtered query: {result['original_query']}")

def test_unsupported_language_uses_spanish_explanation():
    engine = AssistantEngine(ROOT / "knowledge_base")
    result = engine.process_query("zzzz_question_without_knowledge_topic_12345", language="de")
    assert result["status"] == "success"
    assert result["language"] == "es"
    assert result["matched_term"] is None
    assert result["explanation"].startswith("Todavía no tengo una explicación")


def test_offline_questions_do_not_echo_secret_identifiers():
    engine = AssistantEngine(ROOT / "knowledge_base")
    result = engine.process_query("Mi correo test@example.com; ¿cómo uso git?", language="es")
    assert "test@example.com" not in result["original_query"]
    assert "[CONFIDENCIAL]" in result["original_query"]


if __name__ == "__main__":
    test_engine()
    test_unsupported_language_uses_spanish_explanation()
    test_offline_questions_do_not_echo_secret_identifiers()
