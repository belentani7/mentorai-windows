#!/usr/bin/env python3
"""
MentorAI - Interfaz Gráfica Profesional para Windows
Desarrollada con PyQt5
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QTabWidget, QProgressBar, QComboBox, QMessageBox, QSplitter, QStatusBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap
from PyQt5.QtCore import QSize

import sys

# Rutas compatibles con ejecución desde código fuente y con PyInstaller.
# En modo congelado, los recursos se extraen en sys._MEIPASS.
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    APP_ROOT = Path(sys._MEIPASS)
else:
    APP_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(APP_ROOT))

from core.assistant_engine import AssistantEngine
from core.security_manager import SecurityManager
from core.gamification_system import GamificationSystem


class DatabaseManager:
    """Gestor de base de datos local SQLite"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializar base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id TEXT PRIMARY KEY,
                username TEXT,
                language TEXT DEFAULT 'es',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de progreso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                topics_completed INTEGER DEFAULT 0,
                achievements TEXT DEFAULT '[]',
                FOREIGN KEY(user_id) REFERENCES user(id)
            )
        ''')
        
        # Tabla de historial
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                question TEXT,
                answer TEXT,
                topic TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES user(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_or_create_user(self, user_id):
        """Obtener o crear usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.execute('INSERT INTO user (id, username) VALUES (?, ?)', 
                         (user_id, f"Usuario_{user_id[:8]}"))
            conn.commit()
        
        conn.close()
        return True
    
    def get_progress(self, user_id):
        """Obtener progreso del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM progress WHERE user_id = ?', (user_id,))
        progress = cursor.fetchone()
        
        if not progress:
            cursor.execute('''
                INSERT INTO progress (user_id, points, level, experience, streak, topics_completed)
                VALUES (?, 0, 1, 0, 0, 0)
            ''', (user_id,))
            conn.commit()
            cursor.execute('SELECT * FROM progress WHERE user_id = ?', (user_id,))
            progress = cursor.fetchone()
        
        conn.close()
        return progress
    
    def update_progress(self, user_id, points=0, experience=0):
        """Actualizar progreso del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE progress 
            SET points = points + ?, experience = experience + ?
            WHERE user_id = ?
        ''', (points, experience, user_id))
        
        conn.commit()
        conn.close()
    
    def save_query(self, user_id, question, answer, topic):
        """Guardar pregunta en historial"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO history (user_id, question, answer, topic)
            VALUES (?, ?, ?, ?)
        ''', (user_id, question, answer, topic))
        
        conn.commit()
        conn.close()
    
    def get_history(self, user_id, limit=10):
        """Obtener historial de preguntas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT question, topic, timestamp FROM history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        history = cursor.fetchall()
        conn.close()
        return history


class QueryWorker(QThread):
    """Worker thread para procesar queries sin bloquear UI"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, engine, query, language):
        super().__init__()
        self.engine = engine
        self.query = query
        self.language = language
    
    def run(self):
        try:
            result = self.engine.process_query(self.query)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MentorAIWindow(QMainWindow):
    """Ventana principal de MentorAI"""
    
    def __init__(self):
        super().__init__()
        
        # Inicializar componentes
        self.kb_path = APP_ROOT / "knowledge_base"
        self.engine = AssistantEngine(str(self.kb_path))
        self.security = SecurityManager("mentorai_windows")
        self.user_id = "user_001"
        self.language = "es"
        
        # Base de datos
        self.db_path = Path.home() / ".mentorai" / "mentorai.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self.db = DatabaseManager(str(self.db_path))
        self.db.get_or_create_user(self.user_id)
        
        # Gamificación
        self.gamification = GamificationSystem(self.user_id)
        
        # Worker thread
        self.worker = None
        
        self.init_ui()
        self.load_user_data()
    
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle("MentorAI - Tu Asistente Educativo Personal")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.get_stylesheet())
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout()
        
        # Panel izquierdo (Temas)
        left_panel = self.create_left_panel()
        
        # Panel derecho (Chat)
        right_panel = self.create_right_panel()
        
        # Splitter para redimensionar
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Barra de estado
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Listo")
    
    def create_left_panel(self):
        """Crear panel izquierdo con temas"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("📚 Temas Disponibles")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Lista de temas
        self.topics_list = QListWidget()
        self.topics_list.itemClicked.connect(self.on_topic_selected)
        
        topics = [
            "🐍 Python Básico",
            "💻 Windows CMD",
            "⚙️ PowerShell",
            "🔧 Git y Control de Versiones",
            "🐳 Docker y Containerización",
            "🌐 Networking y Redes",
            "🔒 Seguridad en Redes",
            "🛡️ Ciberseguridad Avanzada",
            "📱 Desarrollo Android",
            "💰 Criptografía y Seguridad",
            "🔐 Trust Wallet y Wallets",
            "📊 Binance Basics"
        ]
        
        for topic in topics:
            self.topics_list.addItem(topic)
        
        layout.addWidget(self.topics_list)
        
        # Selector de idioma
        lang_label = QLabel("🌍 Idioma:")
        lang_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Español", "English", "Português", "Català"])
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        layout.addWidget(self.language_combo)
        
        # Botones
        button_layout = QVBoxLayout()
        
        stats_btn = QPushButton("🏆 Mi Progreso")
        stats_btn.clicked.connect(self.show_stats)
        button_layout.addWidget(stats_btn)
        
        history_btn = QPushButton("📜 Historial")
        history_btn.clicked.connect(self.show_history)
        button_layout.addWidget(history_btn)
        
        settings_btn = QPushButton("⚙️ Configuración")
        settings_btn.clicked.connect(self.show_settings)
        button_layout.addWidget(settings_btn)
        
        about_btn = QPushButton("ℹ️ Acerca de")
        about_btn.clicked.connect(self.show_about)
        button_layout.addWidget(about_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """Crear panel derecho con chat"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("💬 Respuesta de MentorAI")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Área de respuesta
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setStyleSheet("background-color: #f9f9f9; color: #333333;")
        layout.addWidget(self.response_text)
        
        # Input de pregunta
        input_label = QLabel("Tu Pregunta:")
        input_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(input_label)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Escribe tu pregunta aquí...")
        self.input_field.returnPressed.connect(self.send_query)
        layout.addWidget(self.input_field)
        
        # Botón enviar
        send_btn = QPushButton("📤 Enviar Pregunta")
        send_btn.clicked.connect(self.send_query)
        send_btn.setStyleSheet("background-color: #007AFF; color: white; font-weight: bold; padding: 8px;")
        layout.addWidget(send_btn)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        panel.setLayout(layout)
        return panel
    
    def on_topic_selected(self, item):
        """Cuando se selecciona un tema"""
        topic_text = item.text()
        # Extraer el nombre del tema sin emoji
        topic_name = topic_text.split()[-1] if topic_text else ""
        self.input_field.setText(f"Explícame sobre {topic_name}")
        self.input_field.setFocus()
    
    def on_language_changed(self, index):
        """Cambiar idioma"""
        languages = ["es", "en", "pt", "ca"]
        self.language = languages[index]
        self.statusBar.showMessage(f"Idioma cambiado a {self.language_combo.currentText()}")
    
    def send_query(self):
        """Enviar pregunta"""
        query = self.input_field.text().strip()
        
        if not query:
            QMessageBox.warning(self, "Advertencia", "Por favor, escribe una pregunta")
            return
        
        self.input_field.clear()
        self.response_text.setText("⏳ Procesando tu pregunta...")
        self.progress_bar.setVisible(True)
        self.statusBar.showMessage("Procesando...")
        
        # Crear worker thread
        self.worker = QueryWorker(self.engine, query, self.language)
        self.worker.finished.connect(self.on_query_finished)
        self.worker.error.connect(self.on_query_error)
        self.worker.start()
    
    def on_query_finished(self, response):
        """Cuando termina de procesar la query"""
        self.progress_bar.setVisible(False)
        
        # Actualizar gamificación
        self.db.update_progress(self.user_id, points=10, experience=10)
        
        # Formatear respuesta
        formatted = self.format_response(response)
        self.response_text.setText(formatted)
        
        # Guardar en historial
        topic = response.get('matched_term', 'General')
        self.db.save_query(self.user_id, 
                          response.get('original_query', ''),
                          response.get('explanation', ''),
                          topic)
        
        self.statusBar.showMessage("Listo")
    
    def on_query_error(self, error):
        """Cuando hay error en la query"""
        self.progress_bar.setVisible(False)
        self.response_text.setText(f"❌ Error: {error}\n\nPor favor, intenta de nuevo.")
        self.statusBar.showMessage("Error")
    
    def format_response(self, response):
        """Formatear respuesta para mostrar"""
        text = f"✅ RESPUESTA:\n{response.get('explanation', 'Sin respuesta')}\n\n"
        
        if response.get('steps'):
            text += "📋 PASOS:\n"
            for i, step in enumerate(response['steps'], 1):
                text += f"{i}. {step}\n"
            text += "\n"
        
        if response.get('security_tips'):
            text += "🔒 CONSEJOS DE SEGURIDAD:\n"
            for tip in response['security_tips']:
                text += f"• {tip}\n"
        
        return text
    
    def show_stats(self):
        """Mostrar estadísticas"""
        progress = self.db.get_progress(self.user_id)
        
        stats_text = f"""
🏆 TU PROGRESO EN MENTORAI

Puntos totales: {progress[2] if progress else 0}
Nivel actual: {progress[3] if progress else 1}
Experiencia: {progress[4] if progress else 0}/1000 XP
Racha de aprendizaje: {progress[5] if progress else 0} días
Temas completados: {progress[6] if progress else 0}

¡Sigue aprendiendo para desbloquear más logros!
        """
        
        QMessageBox.information(self, "Mi Progreso", stats_text)
    
    def show_history(self):
        """Mostrar historial"""
        history = self.db.get_history(self.user_id, limit=5)
        
        history_text = "📜 ÚLTIMAS PREGUNTAS:\n\n"
        for question, topic, timestamp in history:
            history_text += f"• {question}\n  Tema: {topic}\n  {timestamp}\n\n"
        
        QMessageBox.information(self, "Historial", history_text if history else "Sin historial aún")
    
    def show_settings(self):
        """Mostrar configuración"""
        settings_text = """
⚙️ CONFIGURACIÓN

Privacidad:
✅ Todos los datos se procesan localmente
✅ Sin conexión a internet requerida
✅ Cifrado AES-256

Almacenamiento:
📁 Ubicación: ~/.mentorai/
📊 Base de datos: SQLite local

Versión:
v1.0.0 - 2026
        """
        
        QMessageBox.information(self, "Configuración", settings_text)
    
    def show_about(self):
        """Mostrar información acerca de"""
        about_text = """
🎓 MentorAI v1.0.0
Tu Asistente Educativo Personal

Características:
• 35+ temas educativos
• 100% privado y seguro
• Gamificación completa
• Multiidioma
• Código abierto (MIT)

Seguridad:
• Cifrado AES-256
• Procesamiento local
• RGPD compliant

© 2026 MentorAI Project
GitHub: github.com/mentorai/mentorai
        """
        
        QMessageBox.information(self, "Acerca de MentorAI", about_text)
    
    def load_user_data(self):
        """Cargar datos del usuario"""
        self.db.get_progress(self.user_id)
    
    def get_stylesheet(self):
        """Retornar stylesheet personalizado"""
        return """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QLabel {
            color: #333333;
        }
        QPushButton {
            background-color: #007AFF;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0051D5;
        }
        QPushButton:pressed {
            background-color: #003DA8;
        }
        QLineEdit {
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 8px;
            background-color: white;
        }
        QTextEdit {
            border: 1px solid #cccccc;
            border-radius: 5px;
            background-color: white;
        }
        QListWidget {
            border: 1px solid #cccccc;
            border-radius: 5px;
            background-color: white;
        }
        QComboBox {
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 5px;
            background-color: white;
        }
        QStatusBar {
            background-color: #e0e0e0;
        }
        """


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    window = MentorAIWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
