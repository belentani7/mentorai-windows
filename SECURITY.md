# Security Policy — mentorai-windows

## Supported Versions

| Version | Supported |
|---------|-----------|
| main (actual) | Yes       |

## Reporting a Vulnerability

Please report security vulnerabilities by emailing **security@belentani.com** or using GitHub's Private Vulnerability Reporting.

Do NOT create public issues for security vulnerabilities.

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Assessment**: Within 7 days
- **Fix**: Within 30 days (critical), 90 days (non-critical)

## Security Measures

- Secret scanning enabled via gitleaks
- Signed commits required
- Minimum 2 reviewers for merges

<!-- repo-forge:security:inicio -->
# Seguridad

## Reportar una vulnerabilidad

No abras un issue público. Usa el canal privado de GitHub Security del repositorio.
Incluye: versión o commit, pasos para reproducir, impacto y, si puedes, una corrección.

## Qué se considera vulnerabilidad

- Ejecución de código o comandos no previstos.
- Lectura o escritura de archivos fuera del alcance declarado.
- Exposición de credenciales en logs, informes o manifiestos.
- Dependencia con CVE conocido en una ruta ejecutable.

## Reglas del proyecto

- Ningún secreto se escribe en disco, en un log ni en un informe.
- Toda operación de escritura requiere `--apply` explícito.
- Las operaciones destructivas están bloqueadas por diseño.

<!-- repo-forge:security -->
<!-- repo-forge:security:fin -->
