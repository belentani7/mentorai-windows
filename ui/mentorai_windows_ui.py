"""MentorAI para Windows.

Dirección de producto de esta interfaz: profesor calmado, claro y seguro. La
jerarquía prioriza una pregunta a la vez, explicaciones legibles y controles
visibles. El programa no ejecuta comandos, no observa en segundo plano y no
transmite texto o capturas.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QImage, QKeySequence, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRubberBand,
    QShortcut,
    QSplitter,
    QStatusBar,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    APP_ROOT = Path(sys._MEIPASS)
else:
    APP_ROOT = Path(__file__).resolve().parents[1]

if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from core.assistant_engine import AssistantEngine
from core.local_store import LocalStore
from core.screen_orchestrator import ScreenOrchestrator
from native_modules.windows_hotkey import WindowsProfessorHotkey

LANGUAGE_NAMES = {
    "es": "Español",
    "en": "English",
    "pt": "Português",
    "ca": "Català",
}


class QueryWorker(QThread):
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, engine: AssistantEngine, query: str, language: str):
        super().__init__()
        self.engine = engine
        self.query = query
        self.language = language

    def run(self) -> None:
        try:
            self.finished.emit(self.engine.process_query(self.query, self.language))
        except Exception as exc:  # pragma: no cover - defensive UI boundary
            self.failed.emit(str(exc))


class ScreenReadWorker(QThread):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, orchestrator: ScreenOrchestrator, mode: str, image: Any = None):
        super().__init__()
        self.orchestrator = orchestrator
        self.mode = mode
        self.image = image

    def run(self) -> None:
        try:
            if self.mode == "focused":
                result = self.orchestrator.read_focused_text()
            else:
                result = self.orchestrator.read_selected_area(
                    self.image,
                    (0, 0, self.image.width(), self.image.height()),
                )
            self.finished.emit(result)
        except Exception as exc:  # pragma: no cover - defensive UI boundary
            self.failed.emit(str(exc))


class ScreenSelectionOverlay(QWidget):
    """Capa temporal para que el usuario seleccione manualmente una región."""

    selected = pyqtSignal(object)

    def __init__(self, pixmap: QPixmap, geometry):
        super().__init__(None)
        self.pixmap = pixmap
        self.origin = None
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.setGeometry(geometry)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setCursor(Qt.CrossCursor)
        self.setWindowTitle("MentorAI — Selección explícita")

    def paintEvent(self, event):  # noqa: ARG002
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)
        painter.fillRect(self.rect(), QColor(10, 20, 30, 90))
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        painter.drawText(
            24,
            34,
            "MentorAI: arrastra sobre el texto que quieres explicar · Esc para cancelar",
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(self.origin.x(), self.origin.y(), 1, 1)
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.origin is not None:
            self.rubber_band.setGeometry(self._selection_rect(event.pos()))

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton or self.origin is None:
            return
        rect = self._selection_rect(event.pos()).intersected(self.rect())
        self.origin = None
        self.rubber_band.hide()
        if rect.width() < 4 or rect.height() < 4:
            self.close()
            return
        self.selected.emit(self.pixmap.copy(rect))
        self.close()

    def _selection_rect(self, end):
        return self._normalised_rect(self.origin, end)

    @staticmethod
    def _normalised_rect(start, end):
        left, right = sorted((start.x(), end.x()))
        top, bottom = sorted((start.y(), end.y()))
        from PyQt5.QtCore import QRect

        return QRect(left, top, right - left, bottom - top)


class InfoDialog(QDialog):
    def __init__(self, title: str, body: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(620, 460)
        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setPlainText(body)
        layout.addWidget(browser)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class MentorAIWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MentorAIWindow")
        self.setWindowTitle("MentorAI — Profesor local de informática")
        self.resize(1280, 820)
        self.setMinimumSize(960, 640)

        self.kb_path = APP_ROOT / "knowledge_base"
        self.engine = AssistantEngine(self.kb_path)
        self.screen_orchestrator = ScreenOrchestrator()
        self.data_dir = self._data_directory()
        self.store = LocalStore(self.data_dir)
        self.language = self.store.get_language()
        self.worker: QThread | None = None
        self.screen_worker: QThread | None = None
        self.screen_overlay: ScreenSelectionOverlay | None = None
        self.last_response: dict[str, Any] | None = None
        self.last_question = ""

        self._build_ui()
        self._install_shortcuts()
        self.professor_hotkey = WindowsProfessorHotkey(self)
        if QApplication.instance() is not None:
            QApplication.instance().installNativeEventFilter(self.professor_hotkey)
        self.professor_hotkey.register()
        self._populate_topics()
        self._refresh_progress()
        self._apply_language()

    @staticmethod
    def _data_directory() -> Path:
        if os.name == "nt":
            base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
            return base / "MentorAI"
        return Path.home() / ".mentorai"

    def _build_ui(self) -> None:
        self.setStyleSheet(self._stylesheet())
        central = QWidget()
        central.setObjectName("AppSurface")
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QFrame()
        header.setObjectName("TopBar")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(28, 20, 28, 20)
        brand = QLabel("M")
        brand.setObjectName("BrandMark")
        brand.setAccessibleName("Logotipo de MentorAI")
        title_box = QVBoxLayout()
        title = QLabel("MentorAI")
        title.setObjectName("BrandTitle")
        subtitle = QLabel("Un profesor local para entender tu mundo digital")
        subtitle.setObjectName("BrandSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addWidget(brand)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        self.privacy_badge = QLabel("● DATOS LOCALES")
        self.privacy_badge.setObjectName("PrivacyBadge")
        self.language_combo = QComboBox()
        self.language_combo.addItem("Español", "es")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Português", "pt")
        self.language_combo.addItem("Català", "ca")
        self.language_combo.setCurrentIndex(
            max(0, ["es", "en", "pt", "ca"].index(self.language))
        )
        self.language_combo.currentIndexChanged.connect(self._language_changed)
        header_layout.addWidget(self.privacy_badge)
        header_layout.addWidget(self.language_combo)
        outer.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_sidebar())
        splitter.addWidget(self._build_workspace())
        splitter.setSizes([300, 900])
        outer.addWidget(splitter, 1)

        self.status = QStatusBar()
        self.status.setObjectName("StatusBar")
        self.status.showMessage("Listo · procesamiento local")
        self.setStatusBar(self.status)
        self.setCentralWidget(central)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("SideBar")
        sidebar.setMinimumWidth(260)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(12)

        topics_title = QLabel("RUTA DE APRENDIZAJE")
        topics_title.setObjectName("Eyebrow")
        layout.addWidget(topics_title)
        self.topic_search = QLineEdit()
        self.topic_search.setPlaceholderText("Filtrar temas…")
        self.topic_search.setClearButtonEnabled(True)
        self.topic_search.textChanged.connect(self._filter_topics)
        layout.addWidget(self.topic_search)
        self.topics_list = QListWidget()
        self.topics_list.setObjectName("TopicsList")
        self.topics_list.setAccessibleName("Temas educativos disponibles")
        self.topics_list.itemClicked.connect(self._topic_selected)
        layout.addWidget(self.topics_list, 1)

        progress_title = QLabel("TU PROGRESO")
        progress_title.setObjectName("Eyebrow")
        layout.addWidget(progress_title)
        self.progress_label = QLabel("Nivel 1 · 0 XP")
        self.progress_label.setObjectName("ProgressLabel")
        layout.addWidget(self.progress_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setAccessibleName("Progreso hasta el siguiente nivel")
        layout.addWidget(self.progress_bar)

        for text, slot in (
            ("Mi progreso", self.show_stats),
            ("Historial local", self.show_history),
            ("Privacidad y datos", self.show_privacy),
            ("Borrar mis datos", self.delete_local_data),
        ):
            button = QPushButton(text)
            button.setObjectName("QuietButton")
            button.clicked.connect(slot)
            layout.addWidget(button)
        return sidebar

    def _build_workspace(self) -> QWidget:
        workspace = QWidget()
        layout = QVBoxLayout(workspace)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        intro = QLabel("¿Qué quieres entender hoy?")
        intro.setObjectName("WorkspaceTitle")
        layout.addWidget(intro)
        hint = QLabel(
            "Pregunta por pasos concretos. MentorAI explica; tú mantienes el control."
        )
        hint.setObjectName("WorkspaceHint")
        layout.addWidget(hint)

        self.response_text = QTextBrowser()
        self.response_text.setObjectName("ResponsePanel")
        self.response_text.setOpenExternalLinks(True)
        self.response_text.setPlainText(
            "Escribe una pregunta o elige un tema.\n\n"
            "MentorAI trabaja con la base educativa instalada en este equipo. "
            "No ejecuta comandos ni envía tu consulta a un servidor."
        )
        layout.addWidget(self.response_text, 1)

        self.complete_button = QPushButton("Marcar tema como entendido (+50 puntos)")
        self.complete_button.setObjectName("SecondaryButton")
        self.complete_button.setVisible(False)
        self.complete_button.clicked.connect(self._complete_topic)
        layout.addWidget(self.complete_button)

        question_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setObjectName("QuestionInput")
        self.input_field.setPlaceholderText("Ejemplo: ¿qué hace cd en CMD?")
        self.input_field.setClearButtonEnabled(True)
        self.input_field.returnPressed.connect(self.send_query)
        self.input_field.setAccessibleName("Pregunta para MentorAI")
        self.send_button = QPushButton("Preguntar")
        self.send_button.setObjectName("PrimaryButton")
        self.send_button.setMinimumWidth(130)
        self.send_button.clicked.connect(self.send_query)
        question_row.addWidget(self.input_field, 1)
        question_row.addWidget(self.send_button)
        layout.addLayout(question_row)

        professor = QGroupBox("Professor Mode · lectura bajo tu orden")
        professor.setObjectName("ProfessorBox")
        professor_layout = QHBoxLayout(professor)
        professor_hint = QLabel(
            "Atajo Ctrl+Shift+M: congela una imagen temporal y seleccionas el texto. "
            "Esc cancela. No se guarda ni se envía."
        )
        professor_hint.setWordWrap(True)
        professor_hint.setObjectName("ProfessorHint")
        self.focused_button = QPushButton("Leer control enfocado")
        self.focused_button.setObjectName("SecondaryButton")
        self.focused_button.setToolTip(
            "Lee solo el control accesible que tenga el foco"
        )
        self.focused_button.clicked.connect(self.read_focused_control)
        self.area_button = QPushButton("Seleccionar área OCR")
        self.area_button.setObjectName("SecondaryButton")
        self.area_button.setToolTip(
            "Activa una selección manual de pantalla para OCR local opcional"
        )
        self.area_button.clicked.connect(self.arm_professor_mode)
        professor_layout.addWidget(professor_hint, 1)
        professor_layout.addWidget(self.focused_button)
        professor_layout.addWidget(self.area_button)
        layout.addWidget(professor)

        return workspace

    def _install_shortcuts(self) -> None:
        self.ask_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.ask_shortcut.activated.connect(self.send_query)
        self.professor_shortcut = QShortcut(QKeySequence("Ctrl+Shift+M"), self)
        self.professor_shortcut.activated.connect(self.arm_professor_mode)

    def _populate_topics(self, query: str = "") -> None:
        self.topics_list.clear()
        for topic in self.engine.search_topics(query):
            item = QListWidgetItem(f"{topic['label']}\n{topic['category']}")
            item.setData(Qt.UserRole, topic["key"])
            item.setToolTip(f"Preguntar sobre {topic['label']}")
            self.topics_list.addItem(item)

    def _filter_topics(self, query: str) -> None:
        self._populate_topics(query.strip())

    def _topic_selected(self, item: QListWidgetItem) -> None:
        key = str(item.data(Qt.UserRole))
        self.input_field.setText(f"Explícame {key}")
        self.input_field.setFocus()

    def _language_changed(self, index: int) -> None:
        language = str(self.language_combo.itemData(index))
        self.language = language
        self.store.set_language(language)
        self._apply_language()
        self.status.showMessage(f"Idioma de interfaz: {LANGUAGE_NAMES[language]}")

    def _apply_language(self) -> None:
        placeholders = {
            "es": "Ejemplo: ¿qué hace cd en CMD?",
            "en": "Example: what does cd do in CMD?",
            "pt": "Exemplo: o que faz cd no CMD?",
            "ca": "Exemple: què fa cd al CMD?",
        }
        self.input_field.setPlaceholderText(
            placeholders.get(self.language, placeholders["es"])
        )

    def send_query(self) -> None:
        query = self.input_field.text().strip()
        if not query or self.worker is not None and self.worker.isRunning():
            return
        self.last_question = query
        self.input_field.clear()
        self.send_button.setEnabled(False)
        self.response_text.setPlainText("Procesando localmente…")
        self.complete_button.setVisible(False)
        self.status.showMessage("Consultando la base de conocimiento local…")
        self.worker = QueryWorker(self.engine, query, self.language)
        self.worker.finished.connect(self._query_finished)
        self.worker.failed.connect(self._query_failed)
        self.worker.finished.connect(self._release_query_worker)
        self.worker.failed.connect(self._release_query_worker)
        self.worker.start()

    def _release_query_worker(self, *_args) -> None:
        self.send_button.setEnabled(True)
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None

    def _query_finished(self, response: dict) -> None:
        self.last_response = response
        if response.get("status") != "success":
            self.response_text.setPlainText(
                str(response.get("message", "No se pudo procesar la consulta."))
            )
            self.status.showMessage("Consulta no procesada")
            return
        body = self._format_response(response)
        self.response_text.setPlainText(body)
        self.store.record_query(
            response.get("original_query", ""), body, response.get("topic", "General")
        )
        self._refresh_progress()
        self.complete_button.setVisible(bool(response.get("matched_term")))
        self.status.showMessage(
            "Respuesta local lista · nada se ha ejecutado automáticamente"
        )

    def _query_failed(self, message: str) -> None:
        self.response_text.setPlainText(
            f"No se pudo completar la consulta local.\n\nDetalle: {message}"
        )
        self.status.showMessage("Error controlado")

    @staticmethod
    def _format_response(response: dict) -> str:
        lines = [
            "RESPUESTA",
            "",
            str(response.get("explanation", "Sin explicación disponible.")),
            "",
        ]
        steps = response.get("steps") or []
        if steps:
            lines.extend(["PASOS", ""])
            lines.extend(f"{index}. {step}" for index, step in enumerate(steps, 1))
            lines.append("")
        tips = response.get("security_tips") or []
        if tips:
            lines.extend(["SEGURIDAD", ""])
            lines.extend(f"• {tip}" for tip in tips)
            lines.append("")
        lines.extend(["—", str(response.get("safety_notice", "Procesamiento local."))])
        return "\n".join(lines)

    def _complete_topic(self) -> None:
        if not self.last_response:
            return
        topic = str(
            self.last_response.get("matched_term")
            or self.last_response.get("topic")
            or "General"
        )
        self.store.complete_topic(topic)
        self.complete_button.setVisible(False)
        self._refresh_progress()
        self.status.showMessage(f"Tema marcado como entendido: {topic}")

    def _refresh_progress(self) -> None:
        progress = self.store.get_progress()
        current_start = sum(100 * i for i in range(1, progress.level))
        next_start = sum(100 * i for i in range(1, progress.level + 1))
        span = max(1, next_start - current_start)
        percent = max(
            0, min(100, round((progress.points - current_start) / span * 100))
        )
        self.progress_label.setText(
            f"Nivel {progress.level} · {progress.points} puntos · {progress.topics_completed} temas"
        )
        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(f"{percent}%")

    def read_focused_control(self) -> None:
        if self.screen_worker is not None and self.screen_worker.isRunning():
            return
        self.status.showMessage("Leyendo únicamente el control accesible enfocado…")
        self.focused_button.setEnabled(False)
        self.screen_worker = ScreenReadWorker(self.screen_orchestrator, "focused")
        self.screen_worker.finished.connect(self._screen_text_ready)
        self.screen_worker.failed.connect(self._screen_read_failed)
        self.screen_worker.finished.connect(self._release_screen_worker)
        self.screen_worker.failed.connect(self._release_screen_worker)
        self.screen_worker.start()

    def arm_professor_mode(self) -> None:
        if self.screen_overlay is not None:
            return
        screen = QApplication.primaryScreen()
        if screen is None:
            self._screen_read_failed("No se detectó una pantalla disponible.")
            return
        pixmap = screen.grabWindow(0)
        self.screen_overlay = ScreenSelectionOverlay(pixmap, screen.geometry())
        self.screen_overlay.selected.connect(self._area_selected)
        self.screen_overlay.destroyed.connect(self._overlay_closed)
        self.screen_overlay.show()
        self.screen_overlay.raise_()
        self.screen_overlay.activateWindow()
        self.status.showMessage(
            "Professor Mode activo · selecciona manualmente un área o pulsa Esc"
        )

    def _area_selected(self, pixmap: QPixmap) -> None:
        image = pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)
        self.status.showMessage("Área seleccionada · OCR local opcional en curso…")
        self.area_button.setEnabled(False)
        self.screen_worker = ScreenReadWorker(self.screen_orchestrator, "ocr", image)
        self.screen_worker.finished.connect(self._screen_text_ready)
        self.screen_worker.failed.connect(self._screen_read_failed)
        self.screen_worker.finished.connect(self._release_screen_worker)
        self.screen_worker.failed.connect(self._release_screen_worker)
        self.screen_worker.start()

    def _overlay_closed(self) -> None:
        self.screen_overlay = None

    def _release_screen_worker(self, *_args) -> None:
        self.focused_button.setEnabled(True)
        self.area_button.setEnabled(True)
        if self.screen_worker is not None:
            self.screen_worker.deleteLater()
            self.screen_worker = None

    def _screen_text_ready(self, text: str) -> None:
        if not text.strip():
            self.status.showMessage("No se encontró texto accesible.")
            return
        self.input_field.setText(text)
        self.input_field.setFocus()
        self.status.showMessage(
            "Texto leído localmente · revisa y pulsa Preguntar para analizarlo"
        )

    def _screen_read_failed(self, message: str) -> None:
        QMessageBox.warning(self, "Professor Mode", message)
        self.status.showMessage("Lectura cancelada o no disponible")

    def show_stats(self) -> None:
        progress = self.store.get_progress()
        body = (
            f"Nivel: {progress.level}\n"
            f"Puntos: {progress.points}\n"
            f"Experiencia: {progress.experience}\n"
            f"Temas completados: {progress.topics_completed}\n\n"
            "El progreso se guarda en la base local del dispositivo."
        )
        InfoDialog("Mi progreso", body, self).exec_()

    def show_history(self) -> None:
        history = self.store.get_history(30)
        if not history:
            body = "Todavía no hay consultas guardadas en este dispositivo."
        else:
            chunks = []
            for item in history:
                chunks.append(
                    f"[{item.created_at}] {item.topic}\nPregunta: {item.question}\n{item.answer}"
                )
            body = "\n\n".join(chunks)
        InfoDialog("Historial local descifrado", body, self).exec_()

    def show_privacy(self) -> None:
        report = self.store.export_privacy_summary()
        body = (
            "PRIVACIDAD POR DISEÑO\n\n"
            "MentorAI procesa las consultas desde la base instalada. Professor Mode solo se activa por orden explícita; no existe monitorización continua.\n\n"
            f"Ubicación local: {report['database']}\n"
            f"Registros locales: {report['history_records']}\n\n"
            f"Cifrado: {report['security']['encryption']}\n"
            f"Clave: {report['security']['key_protection']}\n\n"
            "No confundas estas garantías técnicas con una certificación jurídica: el lanzamiento comercial requiere revisión de cumplimiento, política de privacidad y pruebas en los dispositivos objetivo."
        )
        InfoDialog("Privacidad y datos", body, self).exec_()

    def delete_local_data(self) -> None:
        answer = QMessageBox.question(
            self,
            "Borrar datos locales",
            "Se eliminarán historial, progreso y la clave local de MentorAI. Esta acción no se puede deshacer. ¿Continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        try:
            self.store.delete_all()
            self.store.reset_profile()
            self._refresh_progress()
            self.response_text.setPlainText(
                "Tus datos locales se han eliminado. MentorAI está listo para empezar de nuevo."
            )
            self.status.showMessage("Datos locales eliminados")
        except Exception as exc:
            QMessageBox.critical(
                self, "No se pudo borrar", f"La operación no terminó: {exc}"
            )

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(1500)
        if self.screen_worker is not None and self.screen_worker.isRunning():
            self.screen_worker.quit()
            self.screen_worker.wait(1500)
        self.professor_hotkey.unregister()
        if QApplication.instance() is not None:
            QApplication.instance().removeNativeEventFilter(self.professor_hotkey)
        event.accept()

    @staticmethod
    def _stylesheet() -> str:
        return """
        * { font-family: 'Segoe UI'; }
        QMainWindow, #AppSurface { background: #f4f1ea; color: #1d2b2a; }
        #TopBar { background: #173b3a; }
        #BrandMark { background: #e2a84b; color: #173b3a; border-radius: 21px; min-width: 42px; max-width: 42px; min-height: 42px; max-height: 42px; font-size: 25px; font-weight: 800; qproperty-alignment: AlignCenter; }
        #BrandTitle { color: #fffaf0; font-size: 23px; font-weight: 700; }
        #BrandSubtitle { color: #bed0c8; font-size: 12px; }
        #PrivacyBadge { color: #c9e2c5; font-size: 11px; font-weight: 700; padding: 8px 12px; border: 1px solid #528a70; border-radius: 6px; }
        #SideBar { background: #e8e4da; border-right: 1px solid #d4cec2; }
        #Eyebrow { color: #56716b; letter-spacing: 1px; font-size: 11px; font-weight: 800; }
        QLineEdit, QComboBox { background: #fffdf8; color: #1d2b2a; border: 1px solid #c8c0b2; border-radius: 5px; padding: 9px 11px; }
        QLineEdit:focus, QComboBox:focus { border: 2px solid #2c7465; padding: 8px 10px; }
        #TopicsList { background: transparent; border: none; outline: none; }
        #TopicsList::item { color: #294540; padding: 10px 8px; border-radius: 5px; margin: 2px 0; }
        #TopicsList::item:hover { background: #d8e1d8; }
        #TopicsList::item:selected { color: #173b3a; background: #c1d4c8; font-weight: 700; }
        #ProgressLabel { color: #294540; font-size: 12px; }
        QProgressBar { background: #d2cec4; border: none; border-radius: 4px; height: 8px; }
        QProgressBar::chunk { background: #2c7465; border-radius: 4px; }
        QPushButton { border-radius: 5px; padding: 10px 14px; font-weight: 700; }
        #QuietButton { background: transparent; color: #31524b; text-align: left; border: 1px solid transparent; }
        #QuietButton:hover { background: #d8e1d8; border-color: #b7cbbd; }
        #WorkspaceTitle { color: #173b3a; font-size: 29px; font-weight: 700; }
        #WorkspaceHint, #ProfessorHint { color: #60736c; font-size: 13px; }
        #ResponsePanel { background: #fffdf8; color: #243b37; border: 1px solid #d4cec2; border-radius: 7px; padding: 18px; font-size: 14px; line-height: 1.45; }
        #QuestionInput { font-size: 15px; padding: 13px; }
        #PrimaryButton { background: #2c7465; color: #ffffff; border: 1px solid #225c50; }
        #PrimaryButton:hover { background: #235f53; }
        #PrimaryButton:disabled { background: #98aaa2; }
        #SecondaryButton { background: #dce8df; color: #234e45; border: 1px solid #b8cdbd; }
        #SecondaryButton:hover { background: #c9ddd0; }
        #ProfessorBox { background: #eaf0e9; border: 1px solid #c0d1c0; border-radius: 7px; color: #234e45; padding: 8px; }
        #StatusBar { background: #e8e4da; color: #56716b; }
        """


def main() -> int:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setApplicationName("MentorAI")
    app.setOrganizationName("MentorAI")
    window = MentorAIWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
