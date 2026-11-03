#!/usr/bin/env python3
"""
Multilingual Testing Suite
Pruebas en Portugués, Español, Inglés y Catalán
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.assistant_engine import AssistantEngine

class MultilingualTester:
    def __init__(self):
        self.engine = AssistantEngine(ROOT / 'knowledge_base')
        if len(self.engine.knowledge_base) < 35:
            raise AssertionError('Base de conocimiento local ausente o incompleta')
        self.results = {
            "portuguese": [],
            "spanish": [],
            "english": [],
            "catalan": []
        }

    def test_portuguese(self):
        """Pruebas en Portugués"""
        print("\n" + "=" * 60)
        print("TESTES EM PORTUGUÊS")
        print("=" * 60)
        
        queries = [
            "O que é cd?",
            "Como mudo de pasta?",
            "O que é Python?",
            "Como uso o PowerShell?",
            "O que é Android?",
        ]
        
        print("\n🇵🇹 Testando consultas em Português:")
        for query in queries:
            result = self.engine.process_query(query, "pt")
            success = result.get("status") == "success" and result.get("matched_term") is not None
            
            print(f"\n  Pergunta: '{query}'")
            print(f"  Resposta: {result.get('explanation', 'N/A')[:60]}...")
            print(f"  Status: {'✓ OK' if success else '✗ Sem informação'}")
            
            self.results["portuguese"].append({
                "query": query,
                "success": success
            })

    def test_spanish(self):
        """Pruebas en Español"""
        print("\n" + "=" * 60)
        print("PRUEBAS EN ESPAÑOL")
        print("=" * 60)
        
        queries = [
            "¿Qué es cd?",
            "¿Cómo cambio de carpeta?",
            "¿Qué es Python?",
            "¿Cómo uso PowerShell?",
            "¿Qué es Android?",
            "¿Cómo me protejo en Binance?",
            "¿Qué es Trust Wallet?",
        ]
        
        print("\n🇪🇸 Probando consultas en Español:")
        for query in queries:
            result = self.engine.process_query(query, "es")
            success = result.get("status") == "success" and result.get("matched_term") is not None
            
            print(f"\n  Pregunta: '{query}'")
            print(f"  Respuesta: {result.get('explanation', 'N/A')[:60]}...")
            print(f"  Estado: {'✓ OK' if success else '✗ Sin información'}")
            
            self.results["spanish"].append({
                "query": query,
                "success": success
            })

    def test_english(self):
        """Pruebas en Inglés"""
        print("\n" + "=" * 60)
        print("TESTS IN ENGLISH")
        print("=" * 60)
        
        queries = [
            "What is cd?",
            "How do I change directory?",
            "What is Python?",
            "How do I use PowerShell?",
            "What is Android?",
            "How do I stay safe on Binance?",
            "What is Trust Wallet?",
        ]
        
        print("\n🇬🇧 Testing queries in English:")
        for query in queries:
            result = self.engine.process_query(query, "en")
            success = result.get("status") == "success" and result.get("matched_term") is not None
            
            print(f"\n  Question: '{query}'")
            print(f"  Answer: {result.get('explanation', 'N/A')[:60]}...")
            print(f"  Status: {'✓ OK' if success else '✗ No information'}")
            
            self.results["english"].append({
                "query": query,
                "success": success
            })

    def test_catalan(self):
        """Pruebas en Catalán"""
        print("\n" + "=" * 60)
        print("PROVES EN CATALÀ")
        print("=" * 60)
        
        queries = [
            "Què és cd?",
            "Com canvio de carpeta?",
            "Què és Python?",
            "Com uso PowerShell?",
            "Què és Android?",
        ]
        
        print("\n🇪🇸 Provant consultes en Català:")
        for query in queries:
            result = self.engine.process_query(query, "ca")
            success = result.get("status") == "success" and result.get("matched_term") is not None
            
            print(f"\n  Pregunta: '{query}'")
            print(f"  Resposta: {result.get('explanation', 'N/A')[:60]}...")
            print(f"  Estat: {'✓ OK' if success else '✗ Sense informació'}")
            
            self.results["catalan"].append({
                "query": query,
                "success": success
            })

    def test_language_switching(self):
        """Probar cambio de idioma en consultas"""
        print("\n" + "=" * 60)
        print("CAMBIO DE IDIOMA EN CONSULTAS")
        print("=" * 60)
        
        print("\n🔄 Mismo concepto en diferentes idiomas:")
        
        queries = {
            "Spanish": ("es", "¿Qué es cd?"),
            "English": ("en", "What is cd?"),
            "Portuguese": ("pt", "O que é cd?"),
            "Catalan": ("ca", "Què és cd?")
        }
        
        for language, (code, query) in queries.items():
            result = self.engine.process_query(query, code)
            print(f"\n  {language}: '{query}'")
            print(f"  Explicación: {result.get('explanation', 'N/A')[:70]}...")

    def test_mixed_language_queries(self):
        """Probar consultas con mezcla de idiomas"""
        print("\n" + "=" * 60)
        print("CONSULTAS CON MEZCLA DE IDIOMAS")
        print("=" * 60)
        
        queries = [
            "What is cd en español?",
            "Cómo uso Python in English?",
            "PowerShell em Português",
            "Android en Català",
        ]
        
        print("\n🌍 Probando consultas mixtas:")
        for query in queries:
            result = self.engine.process_query(query)
            print(f"\n  Consulta: '{query}'")
            print(f"  Resultado: {result.get('explanation', 'N/A')[:60]}...")

    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("\n" + "=" * 60)
        print("PRUEBAS MULTIIDIOMA - MENTORAI")
        print("=" * 60)
        
        self.test_spanish()
        self.test_english()
        self.test_portuguese()
        self.test_catalan()
        self.test_language_switching()
        self.test_mixed_language_queries()
        
        # Contrato comprobable: términos conocidos y mensajes fallback por idioma.
        for code, prefix in (
            ("es", "Todavía no tengo"),
            ("en", "I do not have"),
            ("pt", "Ainda não tenho"),
            ("ca", "Encara no tinc"),
        ):
            known = self.engine.process_query("Python", code)
            assert known["matched_term"] == "python", (code, known)
            unknown = self.engine.process_query(f"zzzxxyy-unknown-{code}", code)
            assert unknown["matched_term"] is None, (code, unknown)
            assert unknown["explanation"].startswith(prefix), (code, unknown)

        # Resumen
        print("\n" + "=" * 60)
        print("RESUMEN DE PRUEBAS MULTIIDIOMA")
        print("=" * 60)
        
        total_by_language = {}
        success_by_language = {}
        
        for language, tests in self.results.items():
            total_by_language[language] = len(tests)
            success_by_language[language] = sum(1 for t in tests if t.get("success", False))
        
        print("\n📊 Resultados por Idioma:")
        print(f"\n{'Idioma':<15} {'Exitosas':<12} {'Total':<8} {'Porcentaje':<10}")
        print("-" * 50)
        
        for language in ["spanish", "english", "portuguese", "catalan"]:
            total = total_by_language.get(language, 0)
            success = success_by_language.get(language, 0)
            percentage = (success / total * 100) if total > 0 else 0
            
            lang_name = {
                "spanish": "Español",
                "english": "English",
                "portuguese": "Português",
                "catalan": "Català"
            }.get(language, language)
            
            print(f"{lang_name:<15} {success:<12} {total:<8} {percentage:.0f}%")
        
        print("\n" + "=" * 60)
        print("CONCLUSIONES MULTIIDIOMA")
        print("=" * 60)
        
        print("\nCobertura de coincidencias reales con temas instalados.")
        print("Una respuesta genérica NO cuenta como explicación encontrada.")
        print("Los mensajes de ausencia de tema se comprueban en ES/EN/PT/CA.")
        print("La traducción del contenido educativo y la accesibilidad UI no se validan aquí.")

        print("\n" + "=" * 60)

if __name__ == "__main__":
    tester = MultilingualTester()
    tester.run_all_tests()
