#!/usr/bin/env python3
"""
MentorAI - Diálogo de Activación de Licencia
Interfaz PyQt5 para activar licencias compradas
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTabWidget, QWidget, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.payment_manager import LicenseManager, StripePaymentProcessor


class LicenseActivationDialog(QDialog):
    """Diálogo para activar licencia"""
    
    license_activated = pyqtSignal(str)  # Emite la clave de licencia
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.license_manager = LicenseManager()
        self.payment_processor = StripePaymentProcessor()
        self.init_ui()
    
    def init_ui(self):
        """Inicializar interfaz"""
        self.setWindowTitle("Activar Licencia - MentorAI")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Activar Licencia
        tab_activate = self.create_activation_tab()
        tabs.addTab(tab_activate, "Activar Licencia")
        
        # Tab 2: Comprar Licencia
        tab_buy = self.create_purchase_tab()
        tabs.addTab(tab_buy, "Comprar Licencia")
        
        # Tab 3: Ver Licencia
        tab_view = self.create_view_tab()
        tabs.addTab(tab_view, "Mi Licencia")
        
        layout.addWidget(tabs)
        
        # Botones
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_activation_tab(self):
        """Crear tab de activación"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Activar tu Licencia")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Instrucciones
        instructions = QLabel(
            "Si ya compraste MentorAI, ingresa tu clave de licencia aquí.\n"
            "La encontrarás en el email de confirmación."
        )
        instructions.setStyleSheet("color: #666666; margin: 10px 0;")
        layout.addWidget(instructions)
        
        # Input de clave
        key_label = QLabel("Clave de Licencia:")
        layout.addWidget(key_label)
        
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("MNT-XXXXXXXXXXXXXXXXXXXXXXXX")
        layout.addWidget(self.license_key_input)
        
        # Input de email
        email_label = QLabel("Email:")
        layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("tu@email.com")
        layout.addWidget(self.email_input)
        
        # Botón activar
        activate_btn = QPushButton("✅ Activar Licencia")
        activate_btn.setStyleSheet("background-color: #34C759; color: white; font-weight: bold; padding: 10px;")
        activate_btn.clicked.connect(self.activate_license)
        layout.addWidget(activate_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_purchase_tab(self):
        """Crear tab de compra"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Comprar MentorAI")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Planes
        plans_text = """
PLANES DISPONIBLES:

🎓 MentorAI Basic - $9.99/año
   • 35+ temas educativos
   • Gamificación completa
   • Funciona offline
   • Multiidioma

⭐ MentorAI Pro - $29.99/año
   • Todo de Basic
   • Actualizaciones automáticas
   • Soporte prioritario
   • Acceso a beta features

🏢 MentorAI Enterprise - $49.99/año
   • Todo de Pro
   • Soporte 24/7
   • Licencia comercial
   • Integración API
        """
        
        plans_label = QLabel(plans_text)
        plans_label.setStyleSheet("background-color: #f9f9f9; padding: 15px; border-radius: 5px;")
        layout.addWidget(plans_label)
        
        # Botón comprar
        buy_btn = QPushButton("💳 Ir a Checkout (Stripe)")
        buy_btn.setStyleSheet("background-color: #007AFF; color: white; font-weight: bold; padding: 10px;")
        buy_btn.clicked.connect(self.open_checkout)
        layout.addWidget(buy_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_view_tab(self):
        """Crear tab para ver licencia actual"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Mi Licencia")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Información de licencia
        self.license_info_text = QTextEdit()
        self.license_info_text.setReadOnly(True)
        self.license_info_text.setStyleSheet("background-color: #f9f9f9;")
        
        license_info = self.license_manager.get_license_info()
        if license_info:
            info_str = f"""
LICENCIA ACTIVADA ✅

Clave: {license_info.get('license_key')}
Email: {license_info.get('email')}
Activada: {license_info.get('activation_date')}
Expira: {license_info.get('expiry_date')}
Estado: {license_info.get('status')}
            """
        else:
            info_str = """
SIN LICENCIA ACTIVADA

No hay licencia activada en este dispositivo.

Opciones:
1. Si ya compraste, activa tu licencia en la pestaña "Activar Licencia"
2. Si no tienes licencia, compra una en "Comprar Licencia"
            """
        
        self.license_info_text.setText(info_str)
        layout.addWidget(self.license_info_text)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        if license_info:
            deactivate_btn = QPushButton("❌ Desactivar")
            deactivate_btn.clicked.connect(self.deactivate_license)
            button_layout.addWidget(deactivate_btn)
        
        renew_btn = QPushButton("🔄 Renovar")
        renew_btn.clicked.connect(self.renew_license)
        button_layout.addWidget(renew_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def activate_license(self):
        """Activar licencia"""
        license_key = self.license_key_input.text().strip()
        email = self.email_input.text().strip()
        
        if not license_key or not email:
            QMessageBox.warning(self, "Error", "Por favor completa todos los campos")
            return
        
        if self.license_manager.validate_license(license_key):
            self.license_manager.activate_license(license_key, email)
            QMessageBox.information(
                self,
                "Éxito",
                f"✅ Licencia activada correctamente!\n\n"
                f"Clave: {license_key}\n"
                f"Email: {email}"
            )
            self.license_activated.emit(license_key)
            self.close()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "❌ Clave de licencia inválida o expirada"
            )
    
    def open_checkout(self):
        """Abrir página de checkout"""
        QMessageBox.information(
            self,
            "Ir a Checkout",
            "Se abrirá tu navegador para completar la compra.\n\n"
            "URL: https://checkout.stripe.com/mentorai\n\n"
            "Después de comprar, recibirás tu clave de licencia por email."
        )
        # En producción: webbrowser.open("https://checkout.stripe.com/...")
    
    def deactivate_license(self):
        """Desactivar licencia"""
        reply = QMessageBox.question(
            self,
            "Desactivar",
            "¿Estás seguro de que quieres desactivar tu licencia?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            license_file = self.license_manager.license_file
            if license_file.exists():
                license_file.unlink()
            QMessageBox.information(self, "Éxito", "Licencia desactivada")
    
    def renew_license(self):
        """Renovar licencia"""
        QMessageBox.information(
            self,
            "Renovar Licencia",
            "Para renovar tu licencia, por favor compra un nuevo plan.\n\n"
            "Haz clic en 'Comprar Licencia' para ver los planes disponibles."
        )
    
    def get_stylesheet(self):
        """Retornar stylesheet"""
        return """
        QDialog {
            background-color: #f9f9f9;
        }
        QLabel {
            color: #333333;
        }
        QLineEdit {
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 8px;
            background-color: white;
        }
        QPushButton {
            border: none;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }
        QTextEdit {
            border: 1px solid #cccccc;
            border-radius: 5px;
        }
        QTabWidget::pane {
            border: 1px solid #cccccc;
        }
        """


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = LicenseActivationDialog()
    dialog.show()
    sys.exit(app.exec_())
