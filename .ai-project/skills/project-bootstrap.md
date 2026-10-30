# 🛠️ Skill: project-bootstrap

## Objetivo

Inicializar y estructurar proyectos nuevos detectando el nivel de completitud de su contexto técnico.

## Protocolo de Ejecución

1. Leer `.ai-project/PROJECT_CONTEXT.md` en la raíz del proyecto.
2. Si el proyecto se encuentra en estado `Draft` o faltan campos obligatorios (Lenguaje, Backend, Frontend, BD):
   - Detener cualquier generación de código.
   - Formular un cuestionario interactivo de 4 a 5 preguntas clave al usuario para definir el stack.
3. Al recibir las respuestas:
   - Actualizar `.ai-project/PROJECT_CONTEXT.md` con el stack definitivo y cambiar el estado a `Active`.
   - Generar la estructura de carpetas inicial basada en las mejores prácticas del framework elegido.
