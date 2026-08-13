#!/usr/bin/env python3
"""
MentorAI - Pruebas del Flujo de Pago y Activación de Licencias
Suite completa de pruebas para validar el sistema de pagos
"""

import sys
import json
import hashlib
import hmac
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.payment_manager import LicenseManager, StripePaymentProcessor


class PaymentFlowTester:
    """Suite de pruebas para el flujo de pago completo"""
    
    def __init__(self):
        self.test_results = []
        self.license_manager = LicenseManager(Path("/tmp/mentorai_test"))
        self.payment_processor = StripePaymentProcessor()
        self.test_count = 0
        self.passed_count = 0
    
    def run_test(self, test_name, test_func):
        """Ejecutar una prueba individual"""
        self.test_count += 1
        try:
            test_func()
            self.test_results.append((test_name, "✅ PASÓ", ""))
            self.passed_count += 1
            print(f"✅ {test_name}")
        except AssertionError as e:
            self.test_results.append((test_name, "❌ FALLÓ", str(e)))
            print(f"❌ {test_name}: {e}")
        except Exception as e:
            self.test_results.append((test_name, "❌ ERROR", str(e)))
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Pruebas de LicenseManager
    
    def test_generate_license_key(self):
        """Prueba: Generar clave de licencia"""
        license_key = self.license_manager.generate_license_key(
            "test@example.com",
            "mentorai_pro"
        )
        assert license_key.startswith("MNT-"), "La clave debe comenzar con MNT-"
        assert len(license_key) == 36, "La clave debe tener 36 caracteres"
    
    def test_activate_license(self):
        """Prueba: Activar licencia"""
        license_key = self.license_manager.generate_license_key(
            "test@example.com",
            "mentorai_pro"
        )
        result = self.license_manager.activate_license(
            license_key,
            "test@example.com",
            days=365
        )
        assert result is True, "La activación debe retornar True"
        
        # Verificar que se guardó correctamente
        license_info = self.license_manager.get_license_info()
        assert license_info is not None, "La información de licencia debe existir"
        assert license_info['license_key'] == license_key, "La clave debe coincidir"
        assert license_info['email'] == "test@example.com", "El email debe coincidir"
    
    def test_validate_license(self):
        """Prueba: Validar licencia activa"""
        license_key = self.license_manager.generate_license_key(
            "test@example.com",
            "mentorai_pro"
        )
        self.license_manager.activate_license(license_key, "test@example.com")
        
        # Validar licencia activa
        is_valid = self.license_manager.validate_license(license_key)
        assert is_valid is True, "La licencia válida debe validarse correctamente"
    
    def test_invalid_license_key(self):
        """Prueba: Rechazar clave de licencia inválida"""
        is_valid = self.license_manager.validate_license("MNT-INVALID")
        assert is_valid is False, "La licencia inválida debe ser rechazada"
    
    def test_expired_license(self):
        """Prueba: Rechazar licencia expirada"""
        license_key = self.license_manager.generate_license_key(
            "test@example.com",
            "mentorai_pro"
        )
        # Activar con 0 días (expira inmediatamente)
        self.license_manager.activate_license(license_key, "test@example.com", days=0)
        
        # Intentar validar
        is_valid = self.license_manager.validate_license(license_key)
        assert is_valid is False, "La licencia expirada debe ser rechazada"
    
    # Pruebas de StripePaymentProcessor
    
    def test_create_payment_session(self):
        """Prueba: Crear sesión de pago"""
        session = self.payment_processor.create_payment_session(
            email="customer@example.com",
            product="mentorai_pro",
            amount=2999
        )
        
        assert 'session_id' in session, "La sesión debe tener un ID"
        assert session['email'] == "customer@example.com", "El email debe coincidir"
        assert session['amount'] == 2999, "El monto debe coincidir"
        assert session['status'] == 'pending', "El estado debe ser pending"
    
    def test_get_products(self):
        """Prueba: Obtener lista de productos"""
        products = self.payment_processor.get_products()
        
        assert len(products) >= 3, "Debe haber al menos 3 productos"
        
        # Verificar estructura de cada producto
        for product in products:
            assert 'id' in product, "El producto debe tener un ID"
            assert 'name' in product, "El producto debe tener un nombre"
            assert 'price' in product, "El producto debe tener un precio"
            assert 'features' in product, "El producto debe tener características"
    
    def test_webhook_processing(self):
        """Prueba: Procesar webhook de Stripe"""
        # Crear datos de webhook simulados
        webhook_data = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer_email': 'webhook@example.com',
                    'payment_status': 'paid'
                }
            }
        }
        
        # Generar firma válida
        signature = hmac.new(
            self.payment_processor.webhook_secret.encode(),
            json.dumps(webhook_data).encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Procesar webhook
        result = self.payment_processor.process_webhook(webhook_data, signature)
        assert result is True, "El webhook debe procesarse correctamente"
        
        # Verificar que la licencia fue activada
        license_info = self.license_manager.get_license_info()
        assert license_info is not None, "La licencia debe haber sido activada por el webhook"
        assert license_info['email'] == 'webhook@example.com', "El email debe coincidir"
    
    def test_invalid_webhook_signature(self):
        """Prueba: Rechazar webhook con firma inválida"""
        webhook_data = {
            'type': 'checkout.session.completed',
            'data': {'object': {'customer_email': 'test@example.com'}}
        }
        
        # Usar una firma inválida
        result = self.payment_processor.process_webhook(webhook_data, "invalid_signature")
        assert result is False, "El webhook con firma inválida debe ser rechazado"
    
    # Pruebas de flujo completo
    
    def test_complete_purchase_flow(self):
        """Prueba: Flujo completo de compra"""
        email = "complete_flow@example.com"
        
        # 1. Crear sesión de pago
        session = self.payment_processor.create_payment_session(
            email=email,
            product="mentorai_pro",
            amount=2999
        )
        assert session['status'] == 'pending', "La sesión debe estar en estado pending"
        
        # 2. Simular pago completado (webhook)
        webhook_data = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer_email': email,
                    'payment_status': 'paid'
                }
            }
        }
        
        signature = hmac.new(
            self.payment_processor.webhook_secret.encode(),
            json.dumps(webhook_data).encode(),
            hashlib.sha256
        ).hexdigest()
        
        result = self.payment_processor.process_webhook(webhook_data, signature)
        assert result is True, "El webhook debe procesarse correctamente"
        
        # 3. Verificar que la licencia está activa
        license_info = self.license_manager.get_license_info()
        assert license_info is not None, "La licencia debe existir"
        assert self.license_manager.validate_license(license_info['license_key']), \
            "La licencia debe ser válida"
    
    def test_multiple_licenses(self):
        """Prueba: Gestionar múltiples licencias"""
        # Nota: En la implementación actual, solo se puede tener una licencia activa
        # Esta prueba verifica que la nueva licencia reemplaza la anterior
        
        license_key_1 = self.license_manager.generate_license_key(
            "user1@example.com",
            "mentorai_basic"
        )
        self.license_manager.activate_license(license_key_1, "user1@example.com")
        
        license_key_2 = self.license_manager.generate_license_key(
            "user2@example.com",
            "mentorai_pro"
        )
        self.license_manager.activate_license(license_key_2, "user2@example.com")
        
        # Verificar que la segunda licencia está activa
        license_info = self.license_manager.get_license_info()
        assert license_info['license_key'] == license_key_2, \
            "La segunda licencia debe estar activa"
    
    def test_license_expiration_date(self):
        """Prueba: Verificar fecha de expiración correcta"""
        license_key = self.license_manager.generate_license_key(
            "expiry@example.com",
            "mentorai_pro"
        )
        
        days = 30
        self.license_manager.activate_license(license_key, "expiry@example.com", days=days)
        
        license_info = self.license_manager.get_license_info()
        expiry_date = datetime.fromisoformat(license_info['expiry_date'])
        activation_date = datetime.fromisoformat(license_info['activation_date'])
        
        delta = expiry_date - activation_date
        assert delta.days == days, f"La diferencia debe ser {days} días"
    
    def test_payment_logging(self):
        """Prueba: Verificar que los pagos se registran"""
        log_file = Path("/tmp/mentorai_test/payments.log")
        
        # Limpiar log anterior
        if log_file.exists():
            log_file.unlink()
        
        # Realizar una activación
        license_key = self.license_manager.generate_license_key(
            "logging@example.com",
            "mentorai_pro"
        )
        self.license_manager.activate_license(license_key, "logging@example.com")
        
        # Verificar que se registró
        assert log_file.exists(), "El archivo de log debe existir"
        with open(log_file, 'r') as f:
            log_content = f.read()
        assert "Licencia activada" in log_content, "El log debe contener la activación"
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("=" * 60)
        print("SUITE DE PRUEBAS: FLUJO DE PAGO Y ACTIVACIÓN DE LICENCIAS")
        print("=" * 60)
        print()
        
        # Pruebas de LicenseManager
        print("📋 PRUEBAS DE LICENSEMANAGER:")
        self.run_test("Generar clave de licencia", self.test_generate_license_key)
        self.run_test("Activar licencia", self.test_activate_license)
        self.run_test("Validar licencia activa", self.test_validate_license)
        self.run_test("Rechazar clave inválida", self.test_invalid_license_key)
        self.run_test("Rechazar licencia expirada", self.test_expired_license)
        print()
        
        # Pruebas de StripePaymentProcessor
        print("💳 PRUEBAS DE STRIPEPAYMENTPROCESSOR:")
        self.run_test("Crear sesión de pago", self.test_create_payment_session)
        self.run_test("Obtener lista de productos", self.test_get_products)
        self.run_test("Procesar webhook", self.test_webhook_processing)
        self.run_test("Rechazar webhook inválido", self.test_invalid_webhook_signature)
        print()
        
        # Pruebas de flujo completo
        print("🔄 PRUEBAS DE FLUJO COMPLETO:")
        self.run_test("Flujo completo de compra", self.test_complete_purchase_flow)
        self.run_test("Gestionar múltiples licencias", self.test_multiple_licenses)
        self.run_test("Verificar fecha de expiración", self.test_license_expiration_date)
        self.run_test("Verificar logging de pagos", self.test_payment_logging)
        print()
        
        # Resumen
        print("=" * 60)
        print(f"RESUMEN: {self.passed_count}/{self.test_count} pruebas pasadas")
        print("=" * 60)
        
        if self.passed_count == self.test_count:
            print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
            return True
        else:
            print(f"❌ {self.test_count - self.passed_count} pruebas fallaron")
            return False


if __name__ == "__main__":
    tester = PaymentFlowTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
