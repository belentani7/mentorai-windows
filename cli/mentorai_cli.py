"""CLI de respaldo de MentorAI.

Comparte exactamente el mismo motor offline y el mismo almacén local que la
interfaz Windows. No ejecuta comandos ni realiza acciones externas.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))

from core.assistant_engine import AssistantEngine
from core.local_store import LocalStore


class MentorAIApp:
    def __init__(self):
        self.engine = AssistantEngine(APP_ROOT / "knowledge_base")
        self.store = LocalStore()
        self.language = self.store.get_language()
        self.running = True

    @staticmethod
    def clear_screen() -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self) -> None:
        print("\n" + "=" * 68)
        print("MENTORAI — profesor local de informática")
        print("Procesamiento local · no ejecuta comandos · sin telemetría")
        print("=" * 68 + "\n")

    def show_main_menu(self) -> str:
        self.clear_screen()
        self.print_header()
        print("1. Hacer una pregunta")
        print("2. Ver temas disponibles")
        print("3. Ver mi progreso")
        print("4. Ver historial local")
        print("5. Ver privacidad")
        print("6. Cambiar idioma")
        print("7. Borrar datos locales")
        print("8. Salir\n")
        return input("Selecciona una opción: ").strip()

    def ask_question(self) -> None:
        self.clear_screen()
        self.print_header()
        question = input("Pregunta (o 'volver'): ").strip()
        if not question or question.casefold() == "volver":
            return
        response = self.engine.process_query(question, self.language)
        if response.get("status") != "success":
            print(f"\nNo se pudo procesar: {response.get('message', 'error')}")
            input("\nPulsa Enter para continuar…")
            return
        body = self.format_response(response)
        print("\n" + body)
        self.store.record_query(
            response.get("original_query", ""), body, response.get("topic", "General")
        )
        if response.get("matched_term"):
            completed = (
                input("\n¿Marcar este tema como entendido? (s/N): ").strip().casefold()
            )
            if completed == "s":
                self.store.complete_topic(str(response["matched_term"]))
        input("\nPulsa Enter para continuar…")

    @staticmethod
    def format_response(response: dict) -> str:
        lines = [
            "RESPUESTA",
            "",
            str(response.get("explanation", "Sin explicación.")),
            "",
        ]
        steps = response.get("steps") or []
        if steps:
            lines.extend(["PASOS", ""])
            lines.extend(f"{i}. {step}" for i, step in enumerate(steps, 1))
            lines.append("")
        tips = response.get("security_tips") or []
        if tips:
            lines.extend(["SEGURIDAD", ""])
            lines.extend(f"- {tip}" for tip in tips)
        return "\n".join(lines)

    def show_topics(self) -> None:
        self.clear_screen()
        self.print_header()
        for topic in self.engine.search_topics():
            print(f"- {topic['label']} ({topic['category']})")
        input("\nPulsa Enter para continuar…")

    def show_progress(self) -> None:
        progress = self.store.get_progress()
        print(
            f"\nNivel {progress.level}\nPuntos: {progress.points}\n"
            f"Experiencia: {progress.experience}\nTemas completados: {progress.topics_completed}"
        )
        input("\nPulsa Enter para continuar…")

    def show_history(self) -> None:
        history = self.store.get_history(10)
        if not history:
            print("\nNo hay historial local.")
        else:
            print("\nHISTORIAL LOCAL")
            for item in history:
                print(f"\n[{item.created_at}] {item.topic}\n{item.question}")
        input("\nPulsa Enter para continuar…")

    def show_privacy(self) -> None:
        report = self.store.export_privacy_summary()
        print("\nPRIVACIDAD")
        print(f"Base local: {report['database']}")
        print(f"Cifrado: {report['security']['encryption']}")
        print(f"Protección de clave: {report['security']['key_protection']}")
        print("Professor Mode: solo bajo activación explícita.")
        input("\nPulsa Enter para continuar…")

    def change_language(self) -> None:
        print("\n1. Español\n2. English\n3. Português\n4. Català")
        value = input("Idioma: ").strip()
        language = {"1": "es", "2": "en", "3": "pt", "4": "ca"}.get(value)
        if language:
            self.language = language
            self.store.set_language(language)

    def clear_local_data(self) -> None:
        confirmation = input(
            "Escribe BORRAR para eliminar historial, progreso y clave: "
        )
        if confirmation == "BORRAR":
            self.store.delete_all()
            self.store.reset_profile()
            self.language = "es"
            print("Datos locales eliminados.")
        else:
            print("Operación cancelada.")
        input("\nPulsa Enter para continuar…")

    def run(self) -> None:
        actions = {
            "1": self.ask_question,
            "2": self.show_topics,
            "3": self.show_progress,
            "4": self.show_history,
            "5": self.show_privacy,
            "6": self.change_language,
            "7": self.clear_local_data,
        }
        while self.running:
            choice = self.show_main_menu()
            if choice == "8":
                self.running = False
            elif choice in actions:
                actions[choice]()


def main() -> int:
    MentorAIApp().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
