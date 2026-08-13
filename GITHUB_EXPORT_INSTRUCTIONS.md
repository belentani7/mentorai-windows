# Instrucciones de Exportación a GitHub y Compilación Windows de MentorAI

Para obtener el archivo `MentorAI.exe` y el instalador `MentorAI-Setup.exe` compilados nativamente para Windows x64, sigue estos pasos:

## 1. Exportar el proyecto a GitHub
1. Abre el panel de administración lateral (Management UI) en la esquina superior derecha.
2. Ve a **Settings** (Configuración) > **GitHub**.
3. Selecciona tu organización o cuenta de propietario, introduce el nombre del repositorio (ej. `mentorai`) y haz clic en **Export to GitHub**.

## 2. Lanzar la compilación automática en GitHub Actions
1. Una vez exportado, abre tu repositorio en [GitHub](https://github.com).
2. Ve a la pestaña **Actions** (Acciones).
3. Selecciona el workflow **Build MentorAI Windows**.
4. Haz clic en **Run workflow** (Ejecutar workflow) y confirma la ejecución en la rama `master` o `main`.

## 3. Descargar los artefactos compilados
1. Cuando el workflow termine con éxito (marcado en verde), entra en la ejecución.
2. En la sección **Artifacts** (Artefactos), descarga el archivo comprimido generado (ej. `MentorAI-Windows-v1.0.0`).
3. Dentro encontrarás:
   - `MentorAI.exe`: El ejecutable principal compilado con PyInstaller para Windows x64.
   - `MentorAI-Setup.exe`: El instalador NSIS para Windows.
   - `SHA256SUMS.txt`: Los hashes de verificación de seguridad.

## 4. Verificación recomendada
* Ejecuta `MentorAI.exe` en una máquina o máquina virtual con Windows 11 limpio para confirmar que la interfaz PyQt5 y la base de conocimiento cargan correctamente sin requerir Python instalado.
