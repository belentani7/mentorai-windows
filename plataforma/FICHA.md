

<!-- repo-forge:plataforma-ficha:inicio -->
# Ficha — MentorAI (`mentorai-windows`)

> Generada por repo-forge el 2026-11-10 desde el árbol real. Cada cifra tiene su fuente en
> [`docs/FUENTES.md`](../docs/FUENTES.md).

## 1. Identidad

| Campo | Valor |
|---|---|
| Repositorio | `belentani7/mentorai-windows` |
| Tipo de plataforma | sitio estático publicable tal cual |
| Modelo de producto | tutor local de informática (CLI + escritorio) |
| Público | personas que aprenden Windows, CMD, Python o Git desde cero, sin conexión fiable |
| Stack medido | Python 58.1%, Markdown 22.5%, JSON 8.2%, HTML 5.4%, JavaScript 2.9%, CSS 1.5% |
| Tamaño | 80 archivos · 9126 líneas · 0.3 MB |

## 2. Máximo potencial

tutor offline con banco de lecciones verificadas, diagnóstico del equipo del alumno y progreso local; el profesor que no necesita internet

Ese es el techo, no el estado. Lo que hoy existe es lo del apartado 3.

## 3. Lo que hay hoy

- Páginas HTML: 3
- Tests: 9
- CI: sí
- Licencia: sí
- README: sí (113 líneas)
- Cumplimiento de reglas: **34/34** (100.0%)

## 4. Diseño de plataforma que la promesa exige

| Módulo | Por qué | Estado |
|---|---|---|
| Motor de lecciones | La promesa lo exige | pendiente |
| Diagnóstico del entorno | La promesa lo exige | pendiente |
| Ejercicios con corrección | La promesa lo exige | pendiente |
| Progreso local | La promesa lo exige | pendiente |
| Exportar apuntes | La promesa lo exige | pendiente |

Datos: lecciones en disco, estado del sistema, progreso.
Integraciones: Ollama opcional, PowerShell.

## 5. Brechas

Ninguna regla en rojo en la última pasada del gate.

## 6. Esfuerzo para llegar al techo

| Fase | Contenido | Días-persona |
|---|---|---|
| 1 | Cerrar reglas en rojo y dejar el gate en verde | 1 |
| 2 | Módulos 1–2 del diseño, con prueba | 15 |
| 3 | Módulos restantes y contenido real | 25 |
| 4 | Pulido, accesibilidad auditada y publicación | 10 |

Supuestos: una persona con contexto del stack, sin bloqueos externos, y sin contar
dependencias de terceros que hoy no estén instaladas.

## 7. Lo que este repositorio no va a hacer

ejecutar comandos destructivos, requerir nube

<!-- repo-forge:ficha -->
<!-- repo-forge:plataforma-ficha:fin -->
