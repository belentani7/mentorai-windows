# Guía de contribución — mentorai-windows

Gracias por interesarte en MentorAI. Este documento describe cómo proponer cambios
sin romper lo que ya funciona.

## Principios

1. **Regresión cero.** Si un cambio rompe algo, se revierte.
2. **Verificar antes que opinar.** Toda afirmación sobre el código debe poder
   reproducirse con un comando.
3. **El núcleo es local.** Ningún cambio debe añadir ejecución remota, telemetría
   ni llamadas de red al motor (`core/`).
4. **Mínima sorpresa.** Respeta las convenciones existentes antes que tu gusto.

## Preparar el entorno

Windows 10/11 con Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-windows.txt
python -m pip install -r requirements-dev.txt
```

Linux (solo para desarrollo y CI; la app objetivo es Windows):

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-windows.txt -r requirements-dev.txt
pip install PyQt5  # ui_smoke necesita QT_QPA_PLATFORM=offscreen y libGL
```

## Antes de enviar un cambio

Ejecuta, como mínimo, desde la raíz del repositorio:

```bash
python -m pytest                    # suite unitaria y de camino feliz
python tests/smoke_runtime.py       # humo del núcleo
python tools/validate_repository.py # validación estructural
python scripts/doctor.py            # reglas del repositorio
```

Si tocas el motor o el cifrado, añade también:

```bash
python tests/security_tests.py
python tests/penetration_testing.py
```

Si tocas la UI, indica en el PR cómo la verificaste (por ejemplo,
`QT_QPA_PLATFORM=offscreen python tests/ui_smoke.py` o captura en Windows 11).

## Estilo

- Python 3.12, type hints donde ya existen, sin dependencias nuevas sin justificar.
- Mensajes de commit convencionales: `type(scope): resumen`
  (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `style`).
- Documentación en español; identificadores de código en inglés como el resto del repo.
- Nunca incluyas secretos, claves ni datos personales en el código ni en los tests.

## Pull requests

- Un PR por tema; diffs pequeños y atómicos.
- Describe el problema, la solución y cómo la verificaste.
- Incluye la salida real de los comandos anteriores en la descripción.
- Revisión requerida: @belentani7 (ver `.github/CODEOWNERS`).

## Reportar una vulnerabilidad

No abras un issue público. Sigue `SECURITY.md` y `.well-known/security.txt`
(GitHub Security Advisories del repositorio).
