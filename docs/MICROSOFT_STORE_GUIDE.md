# 📄 Guía Completa para Publicar MentorAI en Microsoft Store

**Autor:** Manus AI
**Fecha:** 6 de Julio de 2026

## 1. Introducción a Microsoft Store

La Microsoft Store es la plataforma oficial de distribución de aplicaciones para Windows, ofreciendo un vasto alcance a millones de usuarios en todo el mundo. Publicar MentorAI aquí no solo aumenta su visibilidad, sino que también proporciona una capa de confianza y seguridad para los usuarios, ya que todas las aplicaciones pasan por un proceso de certificación.

### ¿Por qué publicar MentorAI en Microsoft Store?

*   **Alcance masivo:** Acceso a una audiencia global de usuarios de Windows.
*   **Confianza del usuario:** Las aplicaciones certificadas por Microsoft inspiran mayor confianza.
*   **Actualizaciones automáticas:** Facilita la distribución de nuevas versiones a los usuarios.
*   **Monetización:** Herramientas integradas para vender licencias y gestionar pagos.
*   **Visibilidad:** Promoción a través de la tienda y sus características.

## 2. Requisitos Previos

Antes de iniciar el proceso de publicación, asegúrate de cumplir con los siguientes requisitos:

### 2.1. Cuenta de Desarrollador de Microsoft

Necesitarás una cuenta de desarrollador de Microsoft activa. Puedes registrarte en el [Centro de Partners de Microsoft](https://partner.microsoft.com/dashboard/windows/overview) [1].

*   **Cuenta Individual:** Para desarrolladores independientes.
*   **Cuenta de Empresa:** Para organizaciones. Requiere verificación adicional.

### 2.2. Certificado de Firma de Código

Para publicar aplicaciones en la Microsoft Store, tu paquete debe estar firmado digitalmente. Aunque la tienda puede firmar automáticamente los paquetes para envíos directos, es una buena práctica tener tu propio certificado de firma de código para mayor control y confianza.

### 2.3. Información de la Empresa/Desarrollador

Prepara la siguiente información:

*   Nombre legal de la empresa/desarrollador.
*   Dirección física.
*   Información de contacto (email, teléfono).
*   Información fiscal (si aplica para la monetización).

## 3. Preparación de la Aplicación (Empaquetado)

MentorAI está desarrollado en Python con PyQt5. Para publicarlo en la Microsoft Store, necesitamos empaquetarlo en un formato compatible, como `.msix` o `.appx`. Utilizaremos `PyInstaller` para crear el ejecutable y luego herramientas adicionales para el empaquetado de la tienda.

### 3.1. Creación del Ejecutable con PyInstaller

Ya hemos compilado el ejecutable `MentorAI-Windows` usando PyInstaller. Este es el binario principal que se incluirá en el paquete de la tienda.

```bash
cd /home/ubuntu/asistente_educativo
pyinstaller --noconsole --onefile --windowed --icon=assets/mentorai.ico ui/mentorai_windows_ui.py
```

**Nota:** Asegúrate de que el archivo `mentorai.ico` esté presente en la carpeta `assets/` y sea un icono de alta resolución.

### 3.2. Empaquetado para Microsoft Store (MSIX)

Microsoft recomienda el formato MSIX para las aplicaciones de la tienda. Puedes usar la herramienta `msix-packaging` de Python para crear el paquete a partir de tu ejecutable PyInstaller.

#### 3.2.1. Instalación de `msix-packaging`

```bash
pip install msix-packaging
```

#### 3.2.2. Creación del Manifiesto de la Aplicación (`AppxManifest.xml`)

Este archivo XML describe tu aplicación. Necesitarás crear uno con la información de MentorAI. Aquí un ejemplo simplificado:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Package
  xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
  xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
  xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
  IgnorableNamespaces="uap rescap">

  <Identity
    Name="[TU_ID_PAQUETE]"
    Publisher="CN=[TU_NOMBRE_EDITOR]"
    Version="1.0.0.0" />

  <Properties>
    <DisplayName>MentorAI</DisplayName>
    <PublisherDisplayName>MentorAI Project</PublisherDisplayName>
    <Logo>Assets\StoreLogo.png</Logo>
  </Properties>

  <Resources>
    <Resource Language="es-ES" />
  </Resources>

  <Dependencies>
    <TargetDeviceFamily Name="Windows.Universal" MinVersion="10.0.17763.0" MaxVersion="10.0.19041.0" />
  </Dependencies>

  <Capabilities>
    <rescap:Capability Name="runFullTrust" />
  </Capabilities>

  <Applications>
    <Application Id="App"
      Executable="MentorAI-Windows.exe"
      EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements
        DisplayName="MentorAI"
        Description="Tu Asistente Educativo Personal"
        BackgroundColor="#007AFF"
        Square150x150Logo="Assets\Square150x150Logo.png"
        Square44x44Logo="Assets\Square44x44Logo.png">
        <uap:DefaultTile>
          <uap:ShowNameOnTiles>
            <uap:ShowOn Tile="square150x150Logo" />
          </uap:ShowNameOnTiles>
        </uap:DefaultTile>
      </uap:VisualElements>
    </Application>
  </Applications>
</Package>
```

**Importante:**
*   `[TU_ID_PAQUETE]`: Un ID único que obtendrás del Centro de Partners.
*   `[TU_NOMBRE_EDITOR]`: El nombre de tu editor, también del Centro de Partners.
*   `Executable`: Debe apuntar a tu ejecutable PyInstaller (`MentorAI-Windows.exe`).
*   `Assets`: Asegúrate de tener los iconos y logos en las dimensiones correctas en una carpeta `Assets`.

#### 3.2.3. Creación del Paquete MSIX

Una vez que tengas el ejecutable y el manifiesto, puedes crear el paquete MSIX:

```bash
msix pack -p AppxManifest.xml -d . -o MentorAI.msix -l Assets
```

Esto creará el archivo `MentorAI.msix` que subirás a la tienda.

### 3.3. Metadatos de la Aplicación

Prepara los siguientes metadatos para tu listado en la tienda:

*   **Nombre del producto:** MentorAI
*   **Descripción:** Una descripción detallada y atractiva de MentorAI, destacando sus características, seguridad y beneficios.
*   **Categoría:** Educación, Herramientas, Productividad.
*   **Palabras clave:** IA, asistente, educación, programación, Windows, seguridad, Python, CMD, PowerShell, Android, cripto.
*   **Edad:** Clasificación por edad (ESRB, PEGI, etc.).
*   **Activos Visuales:**
    *   **Iconos:** Logos de la aplicación en varios tamaños (44x44, 50x50, 71x71, 150x150, 310x150, 310x310 píxeles).
    *   **Capturas de pantalla:** Mínimo 2, máximo 8. Muestra la interfaz de usuario de MentorAI en acción.
    *   **Tráiler (opcional):** Un video corto que muestre las características clave.
*   **Localización:** Proporciona descripciones y metadatos en todos los idiomas que MentorAI soporta (Español, Inglés, Portugués, Catalán).

## 4. Proceso de Envío en el Centro de Partners

Sigue estos pasos para enviar tu aplicación a la Microsoft Store:

### 4.1. Acceder al Centro de Partners

1.  Inicia sesión en el [Centro de Partners de Microsoft](https://partner.microsoft.com/dashboard/windows/overview) [1].
2.  Ve a la sección **Aplicaciones y juegos** y selecciona **Crear una nueva aplicación**.

### 4.2. Configuración del Envío

El proceso de envío se divide en varias secciones:

#### 4.2.1. Precios y Disponibilidad

*   **Precio:** Define el modelo de precios de MentorAI (gratuito, pago único, suscripción). Para MentorAI, se recomienda un modelo de pago único con opción a suscripción para actualizaciones premium.
*   **Mercados:** Selecciona los países donde quieres que MentorAI esté disponible.
*   **Fecha de publicación:** Elige cuándo quieres que la aplicación esté disponible.

#### 4.2.2. Propiedades

*   **Categoría:** Selecciona la categoría principal y subcategoría (ej. Educación > Herramientas de aprendizaje).
*   **Clasificación por edad:** Completa el cuestionario de clasificación por edad para obtener la calificación adecuada.
*   **Características:** Declara las características de tu aplicación (ej. acceso a internet, webcam, etc. - para MentorAI, la mayoría no aplica ya que es offline).

#### 4.2.3. Paquetes

*   **Cargar paquetes:** Sube el archivo `MentorAI.msix` que creaste en el paso 3.2.3.
*   **Pruebas de rendimiento:** La tienda realizará pruebas automáticas en tu paquete.

#### 4.2.4. Listados de la Tienda

*   **Idiomas:** Crea un listado para cada idioma soportado por MentorAI.
*   **Detalles del listado:** Introduce el nombre, descripción, capturas de pantalla, iconos y palabras clave que preparaste en el paso 3.3.

#### 4.2.5. Declaraciones de Cumplimiento

*   **Privacidad:** Proporciona un enlace a la política de privacidad de MentorAI (que debe reflejar su naturaleza offline y segura).
*   **Seguridad:** Declara que MentorAI no recopila datos personales ni realiza acciones no autorizadas.
*   **Criptografía:** Si MentorAI usa cifrado (como AES-256), deberás declararlo.

#### 4.2.6. Notas para el Certificador

Proporciona cualquier información adicional que pueda ayudar al equipo de certificación a revisar tu aplicación. Por ejemplo, si hay alguna funcionalidad específica que deba probarse o si hay alguna limitación conocida.

## 5. Certificación y Publicación

Una vez que hayas completado todos los pasos del envío, tu aplicación entrará en el proceso de certificación de Microsoft.

### 5.1. Proceso de Revisión

El equipo de Microsoft revisará tu aplicación para asegurar que cumple con todas las políticas de la tienda. Esto puede tardar desde unas pocas horas hasta varios días.

### 5.2. Errores Comunes y Cómo Evitarlos

*   **Metadatos incompletos o incorrectos:** Revisa toda la información antes de enviar.
*   **Activos visuales de baja calidad:** Usa imágenes de alta resolución y en los tamaños correctos.
*   **Incumplimiento de políticas de privacidad:** Asegúrate de que tu política de privacidad sea clara y accesible.
*   **Problemas de rendimiento o estabilidad:** Realiza pruebas exhaustivas antes de enviar.

### 5.3. Estado de la Publicación

Recibirás notificaciones sobre el estado de tu aplicación. Una vez aprobada, se publicará en la Microsoft Store.

## 6. Actualizaciones

Para enviar nuevas versiones de MentorAI, simplemente crea un nuevo envío en el Centro de Partners, carga el nuevo paquete MSIX y proporciona las notas de la versión. El sistema de actualizaciones automáticas de MentorAI (implementado en `updater.py`) se encargará de notificar a los usuarios.

## 7. Monetización y Reportes

La Microsoft Store ofrece herramientas para gestionar los precios, las promociones y los reportes de ventas. Podrás ver cuántas descargas tienes, cuántos ingresos generas y de qué mercados provienen.

### 7.1. Integración de Pagos (Stripe)

Aunque la Microsoft Store tiene sus propios métodos de pago, la integración de Stripe en MentorAI (`payment_manager.py`) te permite tener un control más directo sobre las licencias y ofrecer opciones de compra fuera de la tienda si lo deseas. Para la tienda, usarás los mecanismos de compra in-app o de licencia de la propia Microsoft Store.

## 8. Consejos Adicionales

*   **Marketing:** Promociona MentorAI en tus redes sociales, sitio web y otros canales.
*   **Soporte al cliente:** Ofrece un canal de soporte para tus usuarios.
*   **Feedback:** Escucha a tus usuarios y utiliza sus comentarios para mejorar MentorAI.

## 9. Referencias

[1] **Centro de Partners de Microsoft:** [https://partner.microsoft.com/dashboard/windows/overview](https://partner.microsoft.com/dashboard/windows/overview)
[2] **MSIX Packaging Tool:** [https://learn.microsoft.com/en-us/windows/msix/packaging-tool/](https://learn.microsoft.com/en-us/windows/msix/packaging-tool/)
[3] **Políticas de la Microsoft Store:** [https://learn.microsoft.com/en-us/windows/apps/publish/store-policies](https://learn.microsoft.com/en-us/windows/apps/publish/store-policies)
