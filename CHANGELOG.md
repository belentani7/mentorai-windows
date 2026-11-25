# Changelog — mentorai-windows

## [No publicado]

### Corregido (2026-11-25)
- `tests/multilingual_tests.py` y `tests/usability_tests_kid.py`: rutas absolutas
  `/home/ubuntu/asistente_educativo` sustituidas por rutas relativas a la raíz; ambas
  suites ejecutan en cualquier máquina y fallan (exit 1) si falla alguna comprobación.
- `tests/test_payment_flow.py`: el directorio de pruebas pasa de `/tmp/mentorai_test`
  compartido a un `mkdtemp` aislado que se limpia al terminar.
- `core/payment_manager.py`: verificación de firma de webhook en tiempo constante
  (`hmac.compare_digest`), `validate_license` falla en cerrado ante JSON/fechas
  corruptas (sin excepciones al caller), IDs de sesión con `secrets` en lugar de MD5.
- `core/updater.py`: `rollback_update` bloqueado (fail closed); antes ejecutaba
  `shutil.rmtree(app_dir)` sobre el directorio de la aplicación. `except` desnudo
  sustituido por excepciones concretas.
- `core/local_store.py`: descifrado de pregunta y respuesta independiente; un
  registro corrupto ya no oculta el otro campo.
- `core/logger_manager.py`: ruta `/home/ubuntu/asistente_educativo` eliminada del
  demo; `get_all_logs` tolera líneas corruptas.
- `tools/validate_repository.py`: omite `.venv`, `node_modules`, `dist` y demás
  directorios generados (antes reportaba falsos "binarios Windows").
- `scripts/doctor.py`: `catalogo.json` valida el esquema real (`repo`/`familia`/`estado`).
- `.gitignore`: `CONTRIBUTING.md` y `CODE_OF_CONDUCT.md` dejan de ignorarse
  (doctor los exige; ahora existen en el repo).
- `index.html`: título/og reales, meta description útil, stack list relleno con el
  stack real, skip-link, contenido estático (sin JS para el primer pintado),
  URLs absolutas para og:image y canonical.
- `vercel.json`: eliminado el `builds` que referenciaba un `package.json` inexistente
  y el rewrite que enviaba todo a `/site/`; configuración estática con cabeceras de
  seguridad (X-Content-Type-Options, Referrer-Policy, X-Frame-Options,
  Permissions-Policy, Content-Security-Policy).
- CI: runtimes de GitHub Actions migrados a Node 24 (checkout@v7, setup-python@v7,
  upload-artifact@v7, codeql-action@v4, gitleaks-action@v3); `cryptography` del job
  de seguridad fijada al mismo patch que `requirements-windows.txt` (50.0.2; la
  43.0.3 anterior contradecía el pin); clave `permissions` duplicada eliminada;
  workflow `ci.yml` (placeholder) sustituido por una puerta rápida real;
  pasos de pytest y tests de pago añadidos.
- CI: job de gitleaks con `fetch-depth: 0` — con el shallow clone por defecto el
  binario fallaba con exit 1 (no era detección de fugas). `.gitleaks.toml` nuevo:
  allowlist acotada a los fixtures falsos de `tests/smoke_runtime.py` y
  `tests/penetration_testing.py`.

### Seguridad (2026-11-25)
- Comparación de firma de webhook en tiempo constante; licencia corrupta no abre
  el producto; rollback destructivo deshabilitado.

### Rendimiento (2026-11-25)
- `site-hero.js` (bundle React minificado, 147 036 B) retirado del camino crítico:
  el hero es HTML estático + WebGL propio (`hero.js`). Peso de JS de la landing:
  153 539 B → 7 429 B (−95%).
- `hero.js`: degradación elegante cuando WebGL o la compilación fallan,
  `prefers-reduced-motion` pinta un único fotograma, pausa con `visibilitychange`.

### Añadido (2026-11-25)
- `pytest.ini`, `requirements-dev.txt`, `tests/__init__.py`, `tests/unit/__init__.py`.
- Tests nuevos: `test_local_store.py`, `test_payment_manager.py`,
  `test_updater_rollback.py`, `test_e2e_happy_path.py`; `test_engine.py` con asserts.
- `CONTRIBUTING.md` y `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1).
- `Makefile`: `check` = doctor + validador + pytest + humo.
- `site-hero.js` archivado como `archive/prototypes/site-hero.react-bundle.js`.

### Añadido
- AGENTS.md con reglas de desarrollo del proyecto
- .gitleaks.toml con reglas personalizadas para el ecosistema Belentani
- CODEOWNERS con revisión requerida de @belentani7
- SECURITY.md con política de reporte de vulnerabilidades
- CODE_OF_CONDUCT.md (Contributor Covenant 2.1)
- CHANGELOG.md (este archivo)

<!-- repo-forge:changelog:inicio -->
# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Versionado: [SemVer](https://semver.org/lang/es/).

## [No publicado]

### Añadido

- Ficha de máximo potencial, marca, plataforma y fases de monetización (`plataforma/`).
- Banco de datos canónico (`data/`) y doctor de reglas (`scripts/doctor.py`).
- Gobernanza pública: contribución, conducta, seguridad y plantillas de GitHub.

<!-- repo-forge:changelog -->
<!-- repo-forge:changelog:fin -->
