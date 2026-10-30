# 🤖 Directrices del Sistema para Claude (Claude Code / Agent Workflow)

Este proyecto cuenta con un entorno de desarrollo guiado por IA. Antes de realizar cualquier acción, análisis, generación de código o ejecución de comandos, **debes leer e incorporar las reglas definidas en los siguientes documentos del proyecto**:

---

## 1. Contexto y Stack del Proyecto
- **Definición de Arquitectura y Stack:** Consúltalo siempre en `.ai-project/PROJECT_CONTEXT.md`.
  - Si el proyecto está en estado *Draft* o con el stack sin definir, debes iniciar el cuestionario de inicialización con el usuario.
  - Si no se especifica un IDE/editor alternativo, asume **VS Code**.

---

## 2. Protocolos de Ejecución y Terminal
- **Directrices de Shell:** `.ai-project/docs/AI_SHELL_GUIDELINES.md`
  - Ejecuta siempre comandos en modo no interactivo (`npm init -y`, `pip install --no-input`, etc.).
  - Verifica las herramientas instaladas en el sistema antes de lanzar scripts.
  - Registra los despliegues y comandos sensibles en `.ai-project/TEST_SUITE_LOGS.md`.

---

## 3. Protocolo del Sistema de Archivos
- **Operaciones con Ficheros:** `.ai-project/docs/AI_FILE_OPERATIONS.md`
  - Aplica modificaciones mínimas viables mediante parches/diffs.
  - Respeta los archivos protegidos (`.git/`, `.env`, `.ai-project/`, `.ai-project/PROJECT_CONTEXT.md`).
  - Limpia los archivos temporales de pruebas tras finalizar las verificaciones.

---

## 4. Guion de Verificación Inicial (Smoke Tests)
- **Suite de Pruebas:** `.ai-project/docs/VERIFICATION_SUITE.md`
  - Utiliza este documento para validar tus permisos y capacidades de edición/ejecución al arrancar en el proyecto si el usuario lo solicita.

