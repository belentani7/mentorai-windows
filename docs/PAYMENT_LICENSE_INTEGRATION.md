# 📄 Documentación de Integración de Pagos y Licencias de MentorAI

**Autor:** Manus AI
**Fecha:** 6 de Julio de 2026

## 1. Introducción

Este documento detalla la implementación y el funcionamiento del sistema de gestión de licencias y la integración de pagos en MentorAI. El objetivo es proporcionar un mecanismo robusto y seguro para la monetización del producto, permitiendo la venta de licencias y la activación de funcionalidades premium.

El sistema está diseñado para ser flexible, permitiendo tanto la activación de licencias directamente en la aplicación como la integración con plataformas de pago externas como Stripe para la gestión de transacciones.

## 2. Arquitectura General

La gestión de pagos y licencias en MentorAI se basa en dos componentes principales:

1.  **`LicenseManager` (core/payment_manager.py):** Encargado de generar, validar y activar las claves de licencia, así como de almacenar la información de la licencia de forma segura en el dispositivo del usuario.
2.  **`StripePaymentProcessor` (core/payment_manager.py):** Un procesador de pagos simulado que representa la integración con la API de Stripe. En un entorno de producción, este módulo interactuaría directamente con los servicios de Stripe para crear sesiones de pago, verificar transacciones y procesar webhooks.

Ambos módulos están diseñados para operar de forma segura, priorizando la privacidad del usuario y el procesamiento local de datos sensibles.

## 3. `LicenseManager`

El `LicenseManager` es el corazón del sistema de licencias. Se encarga de todas las operaciones relacionadas con la creación, validación y gestión de licencias.

### 3.1. Ubicación del Archivo

`core/payment_manager.py`

### 3.2. Funcionalidades Clave

*   **`generate_license_key(email: str, product_id: str) -> str`:**
    *   Genera una clave de licencia única de 32 caracteres (prefijo `MNT-`) basada en el email del usuario, el ID del producto y un timestamp. Utiliza SHA256 para asegurar la unicidad y seguridad de la clave.
    *   **Uso:** Internamente, para crear nuevas licencias tras una compra exitosa.

*   **`validate_license(license_key: str) -> bool`:**
    *   Verifica si una clave de licencia proporcionada es válida y no ha expirado. Lee la información de la licencia almacenada localmente.
    *   **Uso:** Al iniciar la aplicación o al intentar acceder a funcionalidades premium.

*   **`activate_license(license_key: str, email: str, days: int = 365) -> bool`:**
    *   Activa una licencia, guardando la clave, el email, la fecha de activación y la fecha de expiración (por defecto, 365 días) en un archivo `license.json` dentro del directorio de datos del usuario (`~/.mentorai/`).
    *   **Uso:** Después de una compra exitosa o cuando el usuario introduce manualmente una clave de licencia.

*   **`get_license_info() -> Optional[Dict]`:**
    *   Recupera la información de la licencia activa del archivo `license.json`.
    *   **Uso:** Para mostrar el estado de la licencia al usuario.

*   **`log_payment(message: str)`:**
    *   Registra eventos de pago y activación de licencias en un archivo `payments.log` para auditoría interna.
    *   **Uso:** Para mantener un registro de todas las transacciones y activaciones.

### 3.3. Almacenamiento de Licencias

La información de la licencia se almacena en un archivo JSON (`license.json`) en el directorio de datos del usuario (`~/.mentorai/`). Este archivo contiene:

```json
{
  "license_key": "MNT-XXXXXXXXXXXXXXXXXXXXXXXX",
  "email": "usuario@example.com",
  "activation_date": "2026-07-06T10:00:00.000000",
  "expiry_date": "2027-07-06T10:00:00.000000",
  "status": "active"
}
```

**Consideraciones de Seguridad:**
*   Aunque la clave se almacena localmente, la validación de la licencia puede incluir una verificación con un servidor de licencias remoto en un entorno de producción para prevenir la piratería.
*   El archivo `license.json` debe tener permisos de acceso restringidos para proteger la información del usuario.

## 4. `StripePaymentProcessor`

El `StripePaymentProcessor` simula la interacción con la API de Stripe para gestionar el flujo de pagos. En un entorno de producción, este módulo se conectaría directamente a los servicios de Stripe.

### 4.1. Ubicación del Archivo

`core/payment_manager.py`

### 4.2. Funcionalidades Clave

*   **`create_payment_session(email: str, product: str, amount: int) -> Dict`:**
    *   Simula la creación de una sesión de pago en Stripe. En producción, esto invocaría `stripe.checkout.Session.create()` para generar una URL de pago a la que el usuario sería redirigido.
    *   **Uso:** Cuando el usuario selecciona un plan y procede a la compra.

*   **`verify_payment(session_id: str, payment_intent_id: str) -> bool`:**
    *   Simula la verificación de un pago completado. En producción, esto consultaría la API de Stripe para confirmar el estado de la transacción.
    *   **Uso:** Después de que el usuario completa el pago en la página de checkout de Stripe.

*   **`process_webhook(event_data: Dict, signature: str) -> bool`:**
    *   Simula el procesamiento de un webhook de Stripe. Los webhooks son notificaciones que Stripe envía a tu servidor cuando ocurren eventos importantes (ej. `checkout.session.completed`).
    *   **Uso:** Para activar automáticamente la licencia del usuario una vez que el pago ha sido confirmado por Stripe.

*   **`get_products() -> list`:**
    *   Retorna una lista de productos y sus precios disponibles para MentorAI.
    *   **Uso:** Para mostrar los planes de precios en la interfaz de usuario o en la landing page.

### 4.3. Flujo de Pago (Producción)

El flujo de pago típico con Stripe sería el siguiente:

1.  **Usuario selecciona un plan:** En la aplicación o en la landing page, el usuario elige un plan (ej. MentorAI Pro).
2.  **Crear sesión de pago:** La aplicación llama a `StripePaymentProcessor.create_payment_session()`, que a su vez llama a la API de Stripe. Stripe devuelve una URL de checkout.
3.  **Redirección a Stripe:** La aplicación abre el navegador del usuario y lo redirige a la URL de checkout de Stripe.
4.  **Pago en Stripe:** El usuario completa el pago en la página segura de Stripe.
5.  **Webhook de confirmación:** Una vez que el pago es exitoso, Stripe envía un webhook a un endpoint de tu servidor. Este endpoint invoca `StripePaymentProcessor.process_webhook()`.
6.  **Activación de licencia:** El `process_webhook()` genera y activa la licencia del usuario utilizando `LicenseManager.activate_license()`.
7.  **Confirmación al usuario:** La aplicación puede verificar el estado de la licencia y confirmar al usuario que su compra ha sido exitosa y su licencia está activa.

## 5. Integración con la Interfaz de Usuario (PyQt5)

El módulo `ui/license_activation_dialog.py` proporciona una interfaz gráfica para que los usuarios interactúen con el sistema de licencias y pagos.

### 5.1. Ubicación del Archivo

`ui/license_activation_dialog.py`

### 5.2. Funcionalidades de la UI

*   **Pestaña 
