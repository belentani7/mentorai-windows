# Estructura del Repositorio MentorAI

Este documento define la organización limpia y modular del código fuente, documentación, pruebas e instaladores para garantizar la mantenibilidad y la compilación correcta de MentorAI.

## Mapa de Directorios

```text
mentorai/
├── .github/
│   └── workflows/          # Workflows de CI/CD (GitHub Actions para Windows y tests)
├── cli/                    # Aplicación de línea de comandos y modo diagnóstico
├── core/                   # Núcleo compartido (motor, seguridad, gamificación, pagos)
│   ├── assistant_engine.py
│   ├── gamification_system.py
│   ├── logger_manager.py
│   ├── payment_manager.py
│   ├── screen_orchestrator.py
│   ├── security_manager.py
│   ├── semantic_search_engine.py
│   └── updater.py
├── ui/                     # Interfaces de usuario (PyQt5 Windows UI y diálogos)
│   ├── mentorai_windows_ui.py
│   └── license_activation_dialog.py
├── knowledge_base/         # Módulos de conocimiento educativo (JSON)
├── native_modules/         # Módulos nativos multiplataforma (Accesibilidad/OCR)
├── tests/                  # Suite de pruebas de seguridad, usabilidad, idiomas y pagos
│   └── unit/               # Pruebas unitarias del núcleo
├── tools/                  # Validadores y utilidades de mantenimiento
├── archive/                # Prototipos y scripts legacy conservados, fuera del producto
├── installer/              # Script NSIS oficial para Windows
├── docs/                   # Documentación técnica, manuales y press kit
├── requirements-windows.txt# Dependencias fijadas para empaquetado Windows
├── todo.md                 # Trabajo pendiente y criterios de no-engaño
├── mentorai_windows.spec   # Configuración oficial de PyInstaller
├── README.md               # Documentación principal del proyecto
├── LICENSE.md              # Licencia MIT
└── CONTRIBUTING.md         # Guía de contribución
```

## Criterios de Organización
1. **Separación de responsabilidades:** El núcleo lógico (`core/`) es independiente de la interfaz gráfica (`ui/`) y de los módulos nativos (`native_modules/`).
2. **Eliminación de artefactos inválidos:** El antiguo `dist/` con binarios ELF mal etiquetados fue trasladado fuera del repositorio a `/home/ubuntu/mentorai_quarantine/dist-invalid-previous`; el nuevo repositorio no contiene ejecutables precompilados falsamente etiquetados.
3. **Reproducibilidad:** Las dependencias están congeladas en `requirements-windows.txt` y empaquetadas mediante `mentorai_windows.spec`.
