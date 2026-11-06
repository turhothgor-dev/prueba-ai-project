# Definición del Proyecto y Stack Tecnológico

> **Nota:** Este archivo es leído por los modelos de IA al iniciar cada sesión para comprender el contexto, la arquitectura y las reglas del proyecto actual. Si este archivo está vacío o sin definir, el agente iniciará el cuestionario interactivo de configuración.

---

## 1. Información General del Proyecto

- **Nombre del Proyecto:** MediaOrganizer
- **Descripción Corta:** Aplicación de escritorio para organizar y renombrar archivos de video usando metadatos de TMDB/IMDb
- **Estado:** En Desarrollo

---

## 2. Stack Tecnológico

- **IDE / Editor:** VS Code
- **Lenguaje Principal:** Python 3.11+
- **Framework Backend:** N/A (aplicación de escritorio)
- **Framework Frontend:** PyQt6
- **Base de Datos / ORM:** SQLite (para caché y configuración local)
- **Contenedor / Despliegue:** PyInstaller (ejecutables nativos para Windows, macOS, Linux)

---

## 3. Directrices y Convenciones de Código

- **Estilo de Código:** PEP 8, type hints obligatorios, docstrings en funciones públicas
- **Control de Versiones:** Convención de commits (Ej: Conventional Commits)
- **Notas Especiales / Restricciones:**

  - Arquitectura modular (separar lógica de negocio, GUI y servicios API)
  - Configurable vía archivo JSON/YAML
  - Soporte multiplataforma (Windows, macOS, Linux)

---

## 4. Roadmap del Proyecto

Para el estado actual, tareas completadas y plan de desarrollo, consultar:

📄 **[.ai-project/ROADMAP.md](.ai-project/ROADMAP.md)**

## 5. AI Guidelines

Dentro .ai-project/docs están los documentos de directrices para la IA:

- **[.ai-project\docs\AI_FILE_OPERATIONS.md](.ai-project\docs\AI_FILE_OPERATIONS.md)** Directrices de menjo de archivos.
- **[.ai-project\docs\AI_SHELL_GUIDELINES.md](.ai-project\docs\AI_SHELL_GUIDELINES.md)** Directrices de manejo de comandos del sistema.
- **[.ai-project\docs\VERIFICATION_SUITE.md](.ai-project\docs\VERIFICATION_SUITE.md)** Directrices de verificación.