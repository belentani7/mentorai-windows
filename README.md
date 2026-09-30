# MentorAI para Windows

MentorAI es un **profesor local de informática** para Windows 10/11. Ayuda a comprender informática básica, CMD, PowerShell, Python, Git, Docker, Android, Termux y seguridad digital mediante explicaciones y pasos guiados. No es un agente autónomo: **no ejecuta comandos, no hace clic, no modifica el sistema y no observa la pantalla en segundo plano**.

## Qué funciona en esta versión

La aplicación de escritorio está implementada con PyQt5 y usa una base de conocimiento JSON que se empaqueta junto al ejecutable. Incluye navegación y filtrado de temas, preguntas en lenguaje natural, reconocimiento tolerante de errores de escritura, respuestas con pasos y consejos de seguridad, idioma de interfaz en español, inglés, portugués y catalán, progreso local, historial local cifrado y eliminación explícita de los datos.

El núcleo funciona sin conexión de red. Las consultas y respuestas guardadas se cifran con AES-256-GCM; en Windows, la clave maestra se protege mediante DPAPI para ligarla a la cuenta local. En sistemas que no son Windows existe un fallback restringido para ejecutar pruebas de desarrollo, pero la garantía objetivo del producto Windows se basa en DPAPI.

## Professor Mode

Professor Mode se activa de forma visible mediante el botón **Seleccionar área OCR** o el atajo `Ctrl+Shift+M`. La aplicación congela temporalmente una imagen de la pantalla principal para que el usuario arrastre un rectángulo sobre el texto. Al soltar el botón, el recorte se transforma en memoria y se ofrece al OCR local opcional; no se guarda como archivo ni se sube a un servidor. También existe **Leer control enfocado**, que intenta obtener el nombre y el valor accesible del control que tenga el foco mediante Windows UI Automation.

La acción no es automática ni silenciosa. `Esc` cancela la selección, los controles de contraseña no se leen deliberadamente y el texto detectado solo se coloca en el campo de pregunta: el usuario debe revisarlo y pulsar **Preguntar**. Para disponer de las capacidades opcionales en Windows se pueden instalar los paquetes `uiautomation` y `pytesseract`, además del motor Tesseract OCR con los idiomas necesarios.

## Ejecutar desde código fuente

En Windows 10/11 con Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-windows.txt
python ui\mentorai_windows_ui.py
```

La CLI de respaldo comparte el mismo motor y almacén local:

```powershell
python cli\mentorai_cli.py
```

La aplicación crea sus datos de usuario en `%LOCALAPPDATA%\MentorAI` en Windows. El directorio contiene SQLite local, la clave protegida y los archivos auxiliares de SQLite. No se debe copiar la clave a otro equipo.

## Compilar el ejecutable Windows

La compilación oficial se realiza en un runner `windows-latest` mediante GitHub Actions. El flujo instala las dependencias fijadas, construye `dist\MentorAI.exe` con PyInstaller, comprueba la firma inicial `MZ`, calcula SHA-256 y genera opcionalmente el instalador NSIS. También puede ejecutarse localmente en Windows:

```powershell
python -m PyInstaller --clean --noconfirm mentorai_windows.spec
```

El ejecutable y el instalador no se deben considerar verificados solo por existir o por comenzar con `MZ`: es necesario abrirlos en un Windows 11 limpio, probar consulta, persistencia, Professor Mode, instalación, desinstalación y borrado de datos.

## Pruebas reproducibles

Desde la raíz del repositorio:

```powershell
python tests\smoke_runtime.py
python tests\security_tests.py
python tests\multilingual_tests.py
python tests\usability_tests_kid.py
python tools\validate_repository.py
```

La prueba de humo comprueba carga de la base, búsqueda con errores de escritura, redacción de identificadores sensibles, cifrado autenticado, persistencia y borrado. Las pruebas heredadas de seguridad se conservan como regresión; no sustituyen una auditoría independiente ni un pentest profesional.

## Privacidad, cumplimiento y límites

MentorAI se ha diseñado con minimización de datos, procesamiento local, controles de borrado y activación explícita para pantalla. Eso es una **implementación técnica**, no una certificación jurídica automática. Antes de vender el producto en la Unión Europea hay que completar el inventario de tratamientos, la política de privacidad, la documentación de conservación y borrado, el análisis de riesgos, la revisión de dependencias, la firma de código y las pruebas en dispositivos objetivo con asesoramiento profesional cuando corresponda.

No se incluyen secretos de clientes en el código. Las funciones de pago y licencias permanecen fuera del núcleo offline hasta que exista una integración remota explícita, documentada y protegida; la aplicación local no necesita una cuenta para enseñar los temas instalados.

## Estructura

```text
core/                 Motor, cifrado, persistencia y Professor Mode
ui/                   Aplicación PyQt5 para Windows
cli/                  Interfaz de respaldo que usa el mismo core
knowledge_base/       Temas educativos JSON
native_modules/       Adaptadores de capacidades del sistema
installer/            Script NSIS oficial
tests/                Pruebas ejecutables y unitarias
archive/              Prototipos retirados, no incluidos en el build
```

La estructura completa y sus reglas están documentadas en [`REPOSITORY_STRUCTURE.md`](REPOSITORY_STRUCTURE.md).

---

## Parte del indice educativo

Esta plataforma forma parte del conjunto educativo de **Belentani / NOIACORE**:
formacion gratuita y abierta. El indice completo, con material y estado de cada una,
vive en el nodo central:

**<https://github.com/belentani7/open-school/blob/main/INDICE-EDUCATIVO.md>**

| Plataforma | Que ensena | Enlace |
|---|---|---|
| Open School | Instituto digital universal | https://open-school-gamma.vercel.app |
| ManosAbiertas | IA y ofimatica para recien llegados | https://belentani7.github.io/ManosAbiertas/ |
| WILLIAMSCHOOL | Escuela comunitaria (curriculo Nepal) | https://williamschool.vercel.app |
| UX Academy | Diseno UX/Producto, trilingue | https://ux-academy-professional.vercel.app |
| Aprende Brasil | Educacion para Brasil | https://aprende-brasil.vercel.app/ |
| Lingua Aberta | Idiomas, progresion CEFR | https://belentani7.github.io/lingua-aberta-empresa/ |
| Cruzando el Charco | Acogida y arraigo | https://belentani7.github.io/Cruzando-el-charco/ |
| secure-t | Ciberseguridad e IA | https://belentani7.github.io/secure-t/ |

**PT > ES > EN > CA.** Gratuito, accesible (WCAG) y conectado.
