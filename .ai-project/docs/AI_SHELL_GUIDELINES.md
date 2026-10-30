# Directrices de Ejecución de Comandos Shell para Modelos de IA

Este documento define el protocolo estricto que cualquier agente o modelo de IA (Claude, Qwen, DeepSeek, etc.) debe seguir al interactuar con la terminal o ejecutar comandos en este entorno de desarrollo.

---

## 1. Detección y Adaptación al Entorno

- **Inspección Previa:** Antes de ejecutar comandos de compilación, instalación o despliegue, verifica el SO actual (`uname -a`, `cat /etc/os-release` o variables de entorno) y las herramientas instaladas (`node -v`, `python3 --version`, `docker -v`, etc.).
- **Modo No Interactivo:** Todo comando ejecutado por la IA debe incluir banderas que impidan la pausa por entrada manual de usuario:
  - `npm`: Usar `npm init -y` o `npm install --yes`
  - `apt`: Usar `DEBIAN_FRONTEND=noninteractive apt-get install -y`
  - `pip`: Usar `pip install --no-input`
  - `docker compose`: Usar banderas `-d` para ejecución desacoplada.

---

## 2. Clasificación y Permisos de Comandos

### A. Comandos de Lectura e Inspección (Permitidos sin restricciones)

- Navegación y consulta: `ls`, `tree`, `cat`, `head`, `tail`, `grep`, `find`, `pwd`.
- Estado del sistema y Git: `git status`, `git diff`, `git log`, `env` (filtrando credenciales sensibles).

### B. Comandos de Construcción y Dependencias (Ejecución directa)

- Gestión de paquetes: `npm install`, `pip install -r requirements.txt`, `poetry install`, `cargo build`.
- Linter y Pruebas: `npm test`, `pytest`, `eslint`, `ruff check`.

### C. Comandos Sensibles y Despliegues (Requieren Log / Confirmación)

- Despliegues de infraestructura: `docker compose up`, `kubectl apply`, `terraform apply`, CLI de cloud (AWS, Vercel, Fly.io, etc.).
- Modificaciones destructivas de BD: `prisma migrate dev`, `alembic upgrade`, scripts SQL de alteración/borrado.

---

## 3. Manejo de Errores en Terminal

1. **Revisión de Salida (`stdout` / `stderr`):** Si un comando falla, la IA debe leer el código de salida y el mensaje de error completo antes de intentar una corrección.
2. **Reintentos Contenidos:** No reintentar el mismo comando más de 2 veces sin cambiar los parámetros o pedir asistencia al usuario.
3. **Rollback en Fallo de Deploy:** Si un despliegue falla en mitad del proceso, detener los contenedores o procesos residuales (`docker compose down`) antes de notificar el fallo.

---

## 4. Registro de Operaciones Shell

- Los comandos de despliegue o cambios de entorno importantes deben registrarse en el archivo `.ai-project/TEST_SUITE_LOGS.md` con su fecha, comando ejecutado y resultado.
