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
    assert result['status'] == 'success'
    assert result['matched_term'] == 'cd'
    assert result['steps'], "El tema cd debe ofrecer pasos"

    # Test case 2: Crypto Security
    print("\nTesting 'Binance' security:")
    result = engine.process_query("Quiero entrar en Binance")
    print(f"Security Tips: {result['security_tips']}")
    assert result['status'] == 'success'
    assert result['security_tips'], "La respuesta debe incluir consejos de seguridad"

    # Test case 3: Sensitive data filtering
    print("\nTesting sensitive data filtering:")
    sensitive_text = "Mi clave es 1234-5678-9012-3456 y mi correo es test@example.com"
    result = engine.process_query(sensitive_text)
    print(f"Filtered query: {result['original_query']}")
    assert 'test@example.com' not in result['original_query']
    assert '1234-5678-9012-3456' not in result['original_query']


if __name__ == "__main__":
    test_engine()
