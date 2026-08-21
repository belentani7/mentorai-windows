# Professor Mode

Professor Mode es una función de asistencia contextual, no una herramienta de vigilancia ni de automatización. Su regla principal es que **MentorAI solo lee lo que el usuario activa y selecciona de forma visible**.

## Flujo de accesibilidad

El botón **Leer control enfocado** y el atajo `Ctrl+Shift+M` son acciones explícitas. La primera opción consulta el control que tiene el foco mediante Windows UI Automation, si el proveedor `uiautomation` está instalado. MentorAI intenta obtener nombre, valor y texto de ayuda accesible, pero evita controles identificados como contraseñas. Si Windows no expone texto accesible, la aplicación lo comunica en lugar de inventarlo.

## Flujo de selección y OCR

El botón **Seleccionar área OCR** congela temporalmente la pantalla principal y muestra una capa de selección. El usuario arrastra un rectángulo y puede cancelar con `Esc`. El recorte se mantiene en memoria, se convierte a una imagen temporal y se entrega al OCR local opcional. No se crea un PNG en disco, no se registra la imagen en el historial y no se realiza ninguna petición HTTP.

El texto resultante se copia al campo de pregunta. La aplicación no lo analiza automáticamente: el usuario lo revisa, puede borrarlo o modificarlo y solo entonces pulsa **Preguntar**.

## Dependencias opcionales

`uiautomation` y `pytesseract` se incluyen en los requisitos Python de Windows. Tesseract OCR es un componente externo que debe instalarse por separado en la máquina Windows y debe contar con los paquetes de idioma que el usuario quiera utilizar. Si el componente no está disponible, la aplicación sigue arrancando y muestra una explicación controlada; nunca sustituye el texto por una captura remota.

## Límites y controles

Professor Mode no instala un gancho global de teclado, no registra pulsaciones, no hace clic, no escribe en otras aplicaciones, no ejecuta CMD o PowerShell, no conserva capturas y no lee contraseñas deliberadamente. La política de seguridad debe seguir prohibiendo pegar claves privadas, códigos de recuperación, tokens o credenciales en cualquier campo.

La implementación necesita pruebas en Windows 10/11 con escalado de pantalla, múltiples monitores, aplicaciones de escritorio, navegador, controles protegidos, permisos de accesibilidad y ausencia de Tesseract. Una prueba headless en Linux solo comprueba que la UI se construye; no sustituye esas pruebas de campo.
