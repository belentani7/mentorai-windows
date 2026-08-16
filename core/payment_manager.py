#!/usr/bin/env python3
"""
MentorAI - Gestor de Pagos con Stripe
Integración segura de pagos para licencias
"""

import json
import hashlib
import hmac
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict


class LicenseManager:
    """Gestor de licencias y activación"""
    
    def __init__(self, app_dir=None):
        self.app_dir = app_dir or Path.home() / ".mentorai"
        self.app_dir.mkdir(exist_ok=True)
        self.license_file = self.app_dir / "license.json"
        self.payment_log = self.app_dir / "payments.log"
    
    def generate_license_key(self, email: str, product_id: str) -> str:
        """Generar clave de licencia única"""
        data = f"{email}:{product_id}:{datetime.now().isoformat()}"
        license_key = hashlib.sha256(data.encode()).hexdigest()[:32].upper()
        return f"MNT-{license_key}"
    
    def validate_license(self, license_key: str) -> bool:
        """Validar licencia"""
        if not self.license_file.exists():
            return False
        
        with open(self.license_file, 'r') as f:
            license_data = json.load(f)
        
        if license_data.get('license_key') != license_key:
            return False
        
        # Verificar expiración
        expiry = datetime.fromisoformat(license_data.get('expiry_date', ''))
        if datetime.now() > expiry:
            return False
        
        return True
    
    def activate_license(self, license_key: str, email: str, days: int = 365) -> bool:
        """Activar licencia"""
        license_data = {
            'license_key': license_key,
            'email': email,
            'activation_date': datetime.now().isoformat(),
            'expiry_date': (datetime.now() + timedelta(days=days)).isoformat(),
            'status': 'active'
        }
        
        with open(self.license_file, 'w') as f:
            json.dump(license_data, f, indent=2)
        
        self.log_payment(f"Licencia activada: {license_key}")
        return True
    
    def get_license_info(self) -> Optional[Dict]:
        """Obtener información de licencia"""
        if not self.license_file.exists():
            return None
        
        with open(self.license_file, 'r') as f:
            return json.load(f)
    
    def log_payment(self, message: str):
        """Registrar transacción de pago"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.payment_log, 'a') as f:
            f.write(log_entry)


class StripePaymentProcessor:
    """Procesador de pagos con Stripe (simulado para desarrollo)"""
    
    def __init__(self, stripe_key: Optional[str] = None, app_dir=None, webhook_secret: Optional[str] = None):
        self.stripe_key = stripe_key or "sk_test_mentorai_dev"
        self.license_manager = LicenseManager(app_dir=app_dir)
        self.webhook_secret = webhook_secret or "whsec_mentorai_dev"
    
    def create_payment_session(self, email: str, product: str, amount: int) -> Dict:
        """
        Crear sesión de pago Stripe
        
        En producción, esto usaría la API real de Stripe:
        import stripe
        stripe.api_key = self.stripe_key
        session = stripe.checkout.Session.create(...)
        """
        
        session_data = {
            'session_id': f"cs_{hashlib.md5(email.encode()).hexdigest()[:16]}",
            'email': email,
            'product': product,
            'amount': amount,
            'currency': 'USD',
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'payment_url': f"https://checkout.stripe.com/pay/cs_{hashlib.md5(email.encode()).hexdigest()[:16]}"
        }
        
        return session_data
    
    def verify_payment(self, session_id: str, payment_intent_id: str) -> bool:
        """Verificar pago completado"""
        # En producción: stripe.PaymentIntent.retrieve(payment_intent_id)
        self.license_manager.log_payment(f"Pago verificado: {session_id}")
        return True
    
    def process_webhook(self, event_data: Dict, signature: str) -> bool:
        """Procesar webhook de Stripe"""
        # Verificar firma del webhook
        expected_sig = hmac.new(
            self.webhook_secret.encode(),
            json.dumps(event_data).encode(),
            hashlib.sha256
        ).hexdigest()
        
        if signature != expected_sig:
            return False
        
        # Procesar evento
        event_type = event_data.get('type')
        
        if event_type == 'checkout.session.completed':
            session = event_data.get('data', {}).get('object', {})
            email = session.get('customer_email')
            
            # Generar y activar licencia
            license_key = self.license_manager.generate_license_key(email, 'mentorai_pro')
            self.license_manager.activate_license(license_key, email)
            
            self.license_manager.log_payment(f"Webhook procesado: {event_type}")
            return True
        
        return False
    
    def get_products(self) -> list:
        """Obtener lista de productos disponibles"""
        return [
            {
                'id': 'mentorai_basic',
                'name': 'MentorAI Basic',
                'price': 999,  # $9.99 en centavos
                'description': 'Acceso completo a 35+ temas educativos',
                'features': ['35+ temas', 'Gamificación', 'Offline']
            },
            {
                'id': 'mentorai_pro',
                'name': 'MentorAI Pro',
                'price': 2999,  # $29.99
                'description': 'Incluye actualizaciones automáticas y soporte prioritario',
                'features': ['Todo de Basic', 'Actualizaciones', 'Soporte prioritario']
            },
            {
                'id': 'mentorai_enterprise',
                'name': 'MentorAI Enterprise',
                'price': 4999,  # $49.99
                'description': 'Licencia empresarial con soporte dedicado',
                'features': ['Todo de Pro', 'Soporte 24/7', 'Licencia comercial']
            }
        ]


class PaymentUI:
    """Interfaz de usuario para pagos (integrable con PyQt5)"""
    
    def __init__(self, payment_processor: StripePaymentProcessor):
        self.processor = payment_processor
    
    def show_payment_dialog(self, product_id: str) -> bool:
        """Mostrar diálogo de pago"""
        products = {p['id']: p for p in self.processor.get_products()}
        product = products.get(product_id)
        
        if not product:
            return False
        
        # En producción, esto abriría un diálogo PyQt5
        print(f"\n=== COMPRA: {product['name']} ===")
        print(f"Precio: ${product['price']/100:.2f}")
        print(f"Descripción: {product['description']}")
        print(f"Características: {', '.join(product['features'])}")
        
        return True
    
    def show_license_activation(self) -> Optional[str]:
        """Mostrar diálogo de activación de licencia"""
        license_info = self.processor.license_manager.get_license_info()
        
        if not license_info:
            print("No hay licencia activada. Compra una en mentorai.com")
            return None
        
        print(f"\n=== LICENCIA ACTIVADA ===")
        print(f"Email: {license_info.get('email')}")
        print(f"Clave: {license_info.get('license_key')}")
        print(f"Expira: {license_info.get('expiry_date')}")
        
        return license_info.get('license_key')


# Funciones de prueba
def test_payment_flow():
    """Prueba del flujo de pago completo"""
    print("=== PRUEBA DE FLUJO DE PAGO ===\n")
    
    processor = StripePaymentProcessor()
    
    # Crear sesión de pago
    print("1. Creando sesión de pago...")
    session = processor.create_payment_session(
        email="usuario@example.com",
        product="mentorai_pro",
        amount=2999
    )
    print(f"   ✅ Sesión creada: {session['session_id']}")
    
    # Simular webhook de pago completado
    print("\n2. Simulando pago completado...")
    webhook_data = {
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'customer_email': 'usuario@example.com',
                'payment_status': 'paid'
            }
        }
    }
    
    signature = hmac.new(
        processor.webhook_secret.encode(),
        json.dumps(webhook_data).encode(),
        hashlib.sha256
    ).hexdigest()
    
    if processor.process_webhook(webhook_data, signature):
        print("   ✅ Pago procesado correctamente")
    
    # Verificar licencia
    print("\n3. Verificando licencia...")
    license_info = processor.license_manager.get_license_info()
    if license_info and processor.license_manager.validate_license(license_info['license_key']):
        print(f"   ✅ Licencia válida: {license_info['license_key']}")
    
    print("\n=== PRUEBA COMPLETADA ===")


if __name__ == "__main__":
    test_payment_flow()
