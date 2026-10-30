# Guion de Pruebas de Verificación de Capacidades del Agente IA (Smoke Tests)

Este documento contiene un conjunto de pruebas diseñadas para validar que el modelo de IA seleccionado tiene los permisos adecuados, entiende las directrices del entorno y puede interactuar con el sistema de archivos y la terminal de forma segura y eficaz.

---

## 📋 Lista de Comprobación Inicial

### 1. Prueba de Lectura de Contexto y Detección de Stack
- **Prompt a ejecutar con el modelo:**
  > *"Lee los archivos `.ai-project/PROJECT_CONTEXT.md` y `.ai-project/docs/AI_SHELL_GUIDELINES.md`. ¿Qué stack tecnológico está definido para este proyecto y cuáles son las reglas principales para ejecutar comandos en la terminal?"*
- **Criterio de éxito:**
  - El modelo identifica correctamente el stack o avisa de que el proyecto está en estado *Draft* / no definido.
  - Cita correctamente la restricción de usar comandos en modo no interactivo.

---

### 2. Prueba de Gestión de Archivos (Creación, Modificación y Borrado)
- **Prompt a ejecutar con el modelo:**
  > *"Crea un archivo temporal llamado `test_sandbox.js` en la raíz del proyecto con una función simple `suma(a, b)`. Luego modifícalo para añadir una función `resta(a, b)`. Finalmente, elimina el archivo tras confirmar que se ha modificado correctamente."*
- **Criterio de éxito:**
  - El modelo genera el archivo `test_sandbox.js`.
  - Aplica un parche/dif o modificación sobre el archivo conservando el contenido inicial.
  - Elimina `test_sandbox.js` sin tocar ningún otro archivo del proyecto.
  - Respeta las reglas de borrado seguro indicadas en `AI_FILE_OPERATIONS.md`.

---

### 3. Prueba de Ejecución en Terminal y Detección de Entorno
- **Prompt a ejecutar con el modelo:**
  > *"Ejecuta un comando en la terminal para verificar la versión del entorno de ejecución disponible (Node.js, Python o Docker, según corresponda) y registra el resultado en `.ai-project/TEST_SUITE_LOGS.md`."*
- **Criterio de éxito:**
  - El modelo ejecuta el comando en modo no interactivo (ej: `node -v` o `python3 --version`).
  - Escribe o concatena en `.ai-project/TEST_SUITE_LOGS.md` la fecha, el comando y la salida obtenida.

---

### 4. Prueba de Protocolo de Proyecto Nuevo (Cuestionario de Stack)
- **Escenario:** `.ai-project/PROJECT_CONTEXT.md` está recién creado y con campos en blanco (`[Nombre del proyecto]`, etc.).
- **Prompt a ejecutar con el modelo:**
  > *"Revisa el estado de la definición del proyecto en `.ai-project/PROJECT_CONTEXT.md` y dime si necesitamos definir algo antes de empezar a programar."*
- **Criterio de éxito:**
  - El modelo detecta que el stack no ha sido configurado.
  - Formula preguntas interactivas sobre: Lenguaje, Framework Backend/Frontend, BD y confirma que el editor preferido es VS Code.
  - Ofrece rellenar `.ai-project/PROJECT_CONTEXT.md` con las respuestas recopiladas.

---

### 5. Prueba de Simulación de Despliegue / Comandos Sensibles
- **Prompt a ejecutar con el modelo:**
  > *"Simula los pasos necesarios para desplegar este proyecto mediante Docker Compose. ¿Qué comandos deberías ejecutar y qué comprobaciones previas harías según las directrices?"*
- **Criterio de éxito:**
  - El modelo consulta `AI_SHELL_GUIDELINES.md`.
  - Especifica que usará el modo desacoplado (`docker compose up -d`).
  - Advierte que registrará el evento en el archivo de logs antes de completar el proceso.
