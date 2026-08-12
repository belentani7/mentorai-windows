# MentorAI — Correcciones pendientes para Windows

- [ ] Preparar un punto de entrada PyQt5 compatible con empaquetado Windows.
- [ ] Crear un archivo de requisitos reproducible para Windows.
- [ ] Crear configuración de PyInstaller para Windows x64.
- [ ] Crear workflow de GitHub Actions con runner `windows-latest`.
- [ ] Eliminar del paquete cualquier binario ELF/Linux etiquetado como Windows.
- [ ] Construir el ejecutable PE x64 en un entorno Windows real.
- [ ] Verificar que el ejecutable arranca en Windows 11 limpio.
- [ ] Construir un instalador con payload Windows válido.
- [ ] Firmar el ejecutable/instalador o documentar explícitamente que aún no está firmado.
- [ ] Ejecutar pruebas de instalación, desinstalación y arranque.
- [ ] Entregar solo después de verificar el artefacto real y documentar las limitaciones.

## Bloqueos conocidos

- El sandbox actual es Linux; PyInstaller no produce directamente un ejecutable Windows desde este entorno.
- No hay actualmente una carpeta vinculada al equipo Windows del usuario.
- La compilación Windows deberá ejecutarse en un runner Windows o en un equipo Windows real.

## Criterio de no-engaño

No afirmar que existe un ejecutable Windows funcional hasta confirmar que el archivo es PE x64 y que arranca en Windows 11 limpio.

