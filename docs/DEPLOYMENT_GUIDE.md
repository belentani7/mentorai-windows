# Guía de Compilación, Empaquetado y Distribución de MentorAI

Este documento proporciona instrucciones detalladas para compilar, empaquetar y distribuir MentorAI en Windows, Android y plataformas de código abierto como GitHub.

## Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
3. [Compilación para Windows](#compilación-para-windows)
4. [Compilación para Android](#compilación-para-android)
5. [Publicación en GitHub](#publicación-en-github)
6. [Distribución en App Stores](#distribución-en-app-stores)
7. [Verificación de Seguridad Pre-Lanzamiento](#verificación-de-seguridad-pre-lanzamiento)

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalados los siguientes componentes:

**Para Windows y Android:**
- Node.js 18.0 o superior
- npm o pnpm (recomendado: pnpm 8.0+)
- Python 3.9 o superior
- Git 2.30 o superior

**Para Windows específicamente:**
- Visual Studio Build Tools 2022 o superior
- Windows 11 SDK
- PyInstaller (para empaquetar Python como ejecutable)

**Para Android específicamente:**
- Android Studio 2023.1 o superior
- Android SDK (nivel de API 30+)
- Gradle 8.0 o superior
- Java Development Kit (JDK) 11 o superior

---

## Configuración del Entorno de Desarrollo

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/mentorai/mentorai.git
cd mentorai
```

### Paso 2: Instalar Dependencias

```bash
# Instalar dependencias de Node.js
pnpm install

# Instalar dependencias de Python
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Paso 3: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Configuración General
APP_VERSION=1.0.0
APP_NAME=MentorAI
ENVIRONMENT=production

# Configuración de Seguridad
ENCRYPTION_KEY=your_secure_encryption_key_here
DEVICE_ID_SALT=your_device_id_salt_here

# Configuración de Telemetría (Opcional)
TELEMETRY_ENABLED=false
TELEMETRY_ENDPOINT=https://telemetry.mentorai.dev

# Configuración de Actualizaciones
UPDATE_CHECK_ENABLED=true
UPDATE_ENDPOINT=https://updates.mentorai.dev
```

**Nota Importante:** Nunca incluyas claves secretas reales en el repositorio público. Usa GitHub Secrets para almacenarlas de forma segura.

---

## Compilación para Windows

### Paso 1: Compilar la Interfaz de Usuario (React Native for Windows)

```bash
# Navegar al directorio de la UI
cd ui

# Compilar para producción
pnpm build:windows

# El ejecutable se generará en: dist/windows/MentorAI-Setup.exe
```

### Paso 2: Empaquetar el Core de Python

```bash
# Navegar al directorio del core
cd ../core

# Crear un ejecutable con PyInstaller
pyinstaller --onefile --windowed --icon=../assets/icon.ico assistant_engine.py

# El ejecutable se generará en: dist/assistant_engine.exe
```

### Paso 3: Crear el Instalador de Windows

```bash
# Usar NSIS (Nullsoft Scriptable Install System) para crear el instalador
# Asegúrate de tener NSIS instalado

makensis /DVERSION=1.0.0 /DOUTFILE=MentorAI-Setup-1.0.0.exe installer.nsi

# El instalador final se generará como: MentorAI-Setup-1.0.0.exe
```

**Contenido del archivo `installer.nsi` (ejemplo):**

```nsis
; MentorAI Installer Script
!include "MUI2.nsh"
!include "x64.nsh"

Name "MentorAI ${VERSION}"
OutFile "${OUTFILE}"
InstallDir "$PROGRAMFILES\MentorAI"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "Spanish"

Section "Install"
  SetOutPath "$INSTDIR"
  File "dist\windows\MentorAI.exe"
  File "dist\assistant_engine.exe"
  File "knowledge_base\*.json"
  
  CreateDirectory "$SMPROGRAMS\MentorAI"
  CreateShortcut "$SMPROGRAMS\MentorAI\MentorAI.lnk" "$INSTDIR\MentorAI.exe"
  CreateShortcut "$DESKTOP\MentorAI.lnk" "$INSTDIR\MentorAI.exe"
SectionEnd

Section "Uninstall"
  RMDir /r "$INSTDIR"
  RMDir /r "$SMPROGRAMS\MentorAI"
  Delete "$DESKTOP\MentorAI.lnk"
SectionEnd
```

---

## Compilación para Android

### Paso 1: Configurar el Proyecto React Native para Android

```bash
# Navegar al directorio de la UI
cd ui

# Instalar dependencias de Android
npm install

# Generar el archivo de configuración de Gradle
npx react-native init android --template typescript
```

### Paso 2: Compilar el APK

```bash
# Compilar en modo debug (para pruebas)
cd android
./gradlew assembleDebug

# El APK se generará en: app/build/outputs/apk/debug/app-debug.apk

# Compilar en modo release (para distribución)
./gradlew assembleRelease

# El APK se generará en: app/build/outputs/apk/release/app-release.apk
```

### Paso 3: Firmar el APK para Distribución

```bash
# Crear una clave de firma (solo la primera vez)
keytool -genkey -v -keystore mentorai-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias mentorai

# Firmar el APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore mentorai-release-key.jks app/build/outputs/apk/release/app-release.apk mentorai

# Optimizar el APK firmado
zipalign -v 4 app/build/outputs/apk/release/app-release.apk MentorAI-1.0.0-release.apk
```

### Paso 4: Crear el Bundle de Android (AAB)

```bash
# Para distribución en Google Play Store, se recomienda usar Android App Bundle
./gradlew bundleRelease

# El AAB se generará en: app/build/outputs/bundle/release/app-release.aab
```

---

## Publicación en GitHub

### Paso 1: Preparar el Repositorio

```bash
# Asegúrate de que el repositorio esté limpio
git status

# Añadir todos los archivos
git add .

# Realizar el commit inicial
git commit -m "Initial commit: MentorAI v1.0.0 - Complete educational AI assistant"

# Crear una rama de lanzamiento
git checkout -b release/1.0.0

# Crear un tag para la versión
git tag -a v1.0.0 -m "Release version 1.0.0"
```

### Paso 2: Crear el Repositorio en GitHub

1. Ve a [GitHub.com](https://github.com/new)
2. Crea un nuevo repositorio llamado `mentorai`
3. Selecciona "Public" para que sea código abierto
4. NO inicialices con README (ya lo tienes)

### Paso 3: Subir el Código a GitHub

```bash
# Añadir el repositorio remoto
git remote add origin https://github.com/mentorai/mentorai.git

# Subir la rama principal
git push -u origin master

# Subir la rama de lanzamiento
git push -u origin release/1.0.0

# Subir los tags
git push --tags
```

### Paso 4: Crear un Release en GitHub

1. Ve a la pestaña "Releases" en tu repositorio
2. Haz clic en "Create a new release"
3. Selecciona el tag `v1.0.0`
4. Completa el título y descripción del release
5. Adjunta los archivos compilados:
   - `MentorAI-Setup-1.0.0.exe` (Windows)
   - `MentorAI-1.0.0-release.apk` (Android)
   - `app-release.aab` (Android App Bundle)
6. Publica el release

---

## Distribución en App Stores

### Microsoft Store (Windows)

1. **Crear una Cuenta de Desarrollador:**
   - Ve a [Microsoft Partner Center](https://partner.microsoft.com)
   - Crea una cuenta de desarrollador (costo: $19 USD)

2. **Preparar la Aplicación:**
   - Crea un paquete MSIX usando `msix-packaging-tool`
   - Asegúrate de que la aplicación cumpla con los requisitos de Microsoft Store

3. **Enviar para Revisión:**
   - Sube el paquete MSIX a Partner Center
   - Completa el formulario de envío con detalles de la aplicación
   - Espera la revisión (generalmente 1-3 días)

### Google Play Store (Android)

1. **Crear una Cuenta de Desarrollador:**
   - Ve a [Google Play Console](https://play.google.com/console)
   - Crea una cuenta de desarrollador (costo: $25 USD, único pago)

2. **Preparar la Aplicación:**
   - Genera el Android App Bundle (AAB) como se describe arriba
   - Crea capturas de pantalla y descripciones en español
   - Prepara un icono de aplicación de 512x512 píxeles

3. **Enviar para Revisión:**
   - Sube el AAB a Google Play Console
   - Completa toda la información de la aplicación
   - Revisa las políticas de Google Play
   - Envía para revisión (generalmente 1-3 horas)

---

## Verificación de Seguridad Pre-Lanzamiento

Antes de lanzar MentorAI, realiza las siguientes verificaciones de seguridad:

### Escaneo de Dependencias

```bash
# Verificar vulnerabilidades conocidas en dependencias
npm audit
pnpm audit

# Actualizar dependencias vulnerables
npm audit fix
pnpm update
```

### Análisis de Código Estático

```bash
# Usar herramientas como SonarQube o CodeQL
# Ejemplo con ESLint
npx eslint . --ext .ts,.tsx,.js,.jsx

# Ejemplo con Pylint (Python)
pylint core/*.py
```

### Pruebas de Seguridad

```bash
# Ejecutar pruebas unitarias
pnpm test

# Verificar que no hay datos sensibles en el código
git log -p --all -S "password" -- "*.py" "*.js" "*.tsx"
```

### Verificación de Privacidad

- Confirmar que no hay telemetría no consentida
- Verificar que todos los datos se procesan localmente
- Revisar que el cifrado está correctamente implementado
- Auditar los permisos solicitados en Windows y Android

---

## Checklist de Lanzamiento

Antes de lanzar MentorAI, asegúrate de completar todos estos elementos:

- [ ] Código compilado y probado en Windows 11
- [ ] Código compilado y probado en Android 8.0+
- [ ] Todos los tests unitarios pasan
- [ ] Escaneo de seguridad completado
- [ ] Documentación actualizada
- [ ] Press kit finalizado
- [ ] Landing page en línea
- [ ] Repositorio GitHub público
- [ ] Release creado en GitHub con archivos binarios
- [ ] Aplicación enviada a Microsoft Store
- [ ] Aplicación enviada a Google Play Store
- [ ] Comunicado de prensa distribuido
- [ ] Anuncios en redes sociales programados

---

## Soporte Post-Lanzamiento

Después del lanzamiento, mantén el proyecto actualizado:

- Monitorea los reportes de errores en GitHub Issues
- Responde a las preguntas de los usuarios
- Publica actualizaciones de seguridad regularmente
- Expande la base de conocimiento con nuevos temas
- Recopila feedback de la comunidad

---

**Fin de la Guía de Distribución**

*Versión: 1.0*  
*Última actualización: Junio 2026*
