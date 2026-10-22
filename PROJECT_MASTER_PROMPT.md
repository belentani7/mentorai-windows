# PROJECT_MASTER_PROMPT — MENTORAI WINDOWS — profesor local y seguro de informática

**Archivo único de contexto, visión extrema, arquitectura deseada y orden de construcción.**  
**Repositorio:** `belentani7/mentorai-windows` · **Fecha:** 2026-10-22  
**Naturaleza:** marco de producto editable; **no sustituye el código ni certifica funcionalidades**.

## A. Qué es hoy: identidad y evidencia

Aplicación PyQt5 y CLI con un `core/` común; `knowledge_base/` JSON, `native_modules/`, `installer/`, `tests/`. El README documenta modo local, historial cifrado AES-GCM con DPAPI en Windows, OCR puntual activado por gesto, y empaquetado PyInstaller/NSIS. **No es un agente que manipula el PC**.

## B. A qué debe llegar: visión máxima del producto

Convertirlo en **el mejor profesor local para alfabetización digital en Windows**: explica paso a paso sin invadir la privacidad, acompaña a novatos en CMD, PowerShell, Git, Python, Docker y seguridad, con aprendizaje progresivo multilingüe, demostraciones seguras y una experiencia de escritorio pulida.

## C. Experiencia que debe recibir la persona usuaria

- Inicio enfocado en «qué quieres aprender o resolver», niveles por ruta y búsqueda tolerante a errores con ejemplos prácticos, indicaciones de peligro y enlaces a fuentes locales verificadas.
- Tutor accesible con ejemplos que se pueden copiar, guía de terminal **sin ejecución automática**, aprendizaje por microretos y comprobación de comprensión.
- Professor Mode siempre bajo acción del usuario, delimitación visible de región OCR, preview antes de usar, `Esc` para cancelar y no lectura de campos secretos.
- Privacidad visible: modo offline explícito, historial local y botón real de borrar; PT/ES/EN/CA con contenido efectivamente traducido.

## D. Estructuras futuras: ingeniería y sostenibilidad

- Mantener `core/` independiente de `ui/`, `cli/`, `native_modules/`; documentar contratos de consulta, cifrado y progreso.
- SQLite local, AES-256-GCM, clave maestra protegida mediante DPAPI en Windows, sin sincronización a nube por defecto. Pruebas para cifrado, corrupción y borrado de registros.
- Compatibilidad Windows 10/11; empaquetado PyInstaller `mentorai_windows.spec`, CI con `windows-latest`, hashes y firma de código antes de distribución de confianza.
- Local OCR/UI Automation estrictamente opt-in; memoria temporal de pantalla, sin logs de capturas.

## E. Roadmap de construcción por entregables comprobables

1. Ejecutar smoke/security/multilingual/usability y `tools/validate_repository.py`.
2. Perfeccionar flujos PyQt5 y navegación teclado, lectura de pantalla y feedback de errores.
3. Expandir currículo técnico con módulos JSON bien estructurados y ejercicios verificables.
4. Añadir pruebas E2E de instalación/desinstalación en Windows real; verificar DPAPI en dispositivo objetivo.
5. Preparar actualizaciones firmadas y documentación de privacidad solo tras modelo de seguridad verificado.

## F. Fronteras que no deben cruzarse

No declarar certificación legal sin revisión, no instalar comandos autónomos ni capturar pantalla en segundo plano, no usar datos de usuario para entrenar modelos ni convertir en gestor remoto.

## Modo de trabajo para cualquier IA que abra este repositorio

**Lee este archivo antes de escribir código.** Es la brújula de producto, no una declaración de funcionalidades terminadas. Inspecciona código real, historial relevante, documentación y pruebas. Distingue: EXISTE / PARCIAL / PROPUESTA / BLOQUEADA. Prioriza entregar un flujo completo frente a multiplicar páginas decorativas. Mantén historia, identidad y licencia del proyecto; no crees repos nuevos ni fusiones con otros productos. Respeta los datos de usuarios, secretos y límites de permisos. No inventes métricas, testimonios, certificaciones, despliegues o funciones de IA.

**Ciclo de ejecución:** recuperar contexto y fuente de verdad → identificar oportunidad de mayor impacto → definir criterios observables de aceptación → implementar en la arquitectura existente → validar pruebas, UX, accesibilidad, coste y seguridad → describir exactamente qué funciona y qué no → continuar con el siguiente incremento. Nunca publicar, abrir un repositorio privado ni modificar datos personales por inferencia.

**Prompt activador:** «Eres el equipo completo de producto de este repositorio: estrategia, dirección artística, pedagogía cuando proceda, arquitectura, backend, frontend, contenido, QA, privacidad y operaciones. Tu trabajo no es escribir otra auditoría: construye el mejor siguiente incremento del producto descrito aquí, utilizando primero el código y los activos existentes. No diluyas su identidad. Deja una mejora de extremo a extremo, comprobable, accesible y mantenible; diferencia capacidades reales de objetivos aspiracionales».

**Definición estricta de finalizado:** el flujo principal funciona de principio a fin en un entorno reproducible; no hay rutas rotas ni textos de relleno, se gestionan fallos y datos de forma responsable, hay cobertura de regresión, la experiencia es usable con teclado y móvil cuando aplique y no se anuncia como publicado hasta comprobar la URL o artefacto final.
