# MentorAI — Correcciones pendientes para Windows

- [x] Preparar un punto de entrada PyQt5 compatible con empaquetado Windows.
- [x] Crear un archivo de requisitos reproducible para Windows.
- [x] Crear configuración de PyInstaller para Windows x64.
- [x] Crear workflow de GitHub Actions con runner `windows-latest`.
- [x] Marcar el binario ELF anterior como inválido y evitar reutilizarlo en el nuevo instalador.
- [x] Construir el ejecutable PE x64 en un runner Windows real mediante GitHub Actions.
- [ ] Verificar que el ejecutable arranca en Windows 11 limpio.
- [x] Crear script NSIS nuevo con payload `dist\\MentorAI.exe`; falta ejecutarlo en Windows.
- [ ] Firmar el ejecutable/instalador o documentar explícitamente que aún no está firmado.
- [ ] Ejecutar pruebas de instalación, desinstalación y arranque.
- [ ] Entregar solo después de verificar el artefacto real y documentar las limitaciones.

## Bloqueos conocidos

- El sandbox actual es Linux; PyInstaller no produce directamente un ejecutable Windows desde este entorno.
- No hay actualmente una carpeta vinculada al equipo Windows del usuario.
- La compilación Windows deberá ejecutarse en un runner Windows o en un equipo Windows real.

## Criterio de no-engaño

No afirmar que existe un ejecutable Windows funcional hasta confirmar que el archivo es PE x64 y que arranca en Windows 11 limpio.

## Construcción del software Windows real

- [x] Consolidar la aplicación PyQt como punto de entrada único y funcional.
- [x] Corregir las incompatibilidades entre motor, CLI, gamificación y persistencia local.
- [x] Sustituir las afirmaciones de cifrado simulado por almacenamiento local autenticado real o documentar claramente cualquier limitación.
- [x] Implementar Professor Mode con activación explícita y captura local segura; no enviar capturas ni texto fuera del dispositivo.
- [x] Añadir pruebas de arranque, consulta, persistencia, borrado y manejo de datos sensibles.
- [x] Preparar una compilación Windows nativa reproducible y verificar que el artefacto es PE32+ x64.
- [ ] Abrir y validar el instalador y la aplicación en una máquina Windows 11 real vinculada.
- [ ] No declarar el producto como 10/10, listo para vender o conforme legalmente sin pruebas y revisión profesional correspondientes.

