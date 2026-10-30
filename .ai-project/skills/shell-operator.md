# ⚡ Skill: shell-operator

## Objetivo

Garantizar la ejecución de comandos en la terminal de forma autónoma, no interactiva y segura.

## Protocolo de Ejecución

1. Consultar las directrices obligatorias en `.ai-project/docs/AI_SHELL_GUIDELINES.md`.
2. **Flags No Interactivas:** Añadir siempre parámetros de confirmación automática (ej: `npm init -y`, `pip install --no-input`, `docker compose up -d`).
3. **Verificación Previa:** Comprobar la disponibilidad de los CLI necesarios (`node -v`, `docker -v`, etc.) antes de lanzar tareas complejas.
4. **Auditoría:** Concatenar la salida relevante de los comandos de compilación, tests y despliegue en `.ai-project/TEST_SUITE_LOGS.md`.
