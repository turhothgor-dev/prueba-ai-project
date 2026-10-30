# Protocolo de Operaciones sobre el Sistema de Archivos

Este documento especifica las reglas de seguridad y buenas prácticas para la creación, modificación, parcheo y borrado de archivos por parte de modelos de IA en el proyecto.

---

## 1. Principios Generales

- **Persistencia de Contexto:** Antes de crear o editar cualquier archivo del proyecto, consulta `.ai-project/PROJECT_CONTEXT.md` para respetar las convenciones de código, nombres y arquitectura definidas.
- **Edición Mínima Viable:** Prefiere modificar únicamente las partes necesarias de un archivo en lugar de reescribirlo por completo, salvo que el archivo sea completamente nuevo o sufra un refactor integral.
- **Verificación Previa:** Confirma siempre la ruta absoluta o relativa antes de escribir o borrar.

---

## 2. Reglas para Creación de Archivos

1. **Estructura Estándar:** Respeta la arquitectura de carpetas establecida en el proyecto (ej: `src/`, `components/`, `api/`, `tests/`). No crees carpetas raíz arbitrarias.
2. **Archivos de Configuración:** Al generar configuraciones (`package.json`, `Dockerfile`, `tsconfig.json`, etc.), incluye comentarios explicando las elecciones clave si no son convencionales.
3. **Archivos de Entorno:** Nunca guardes credenciales reales en `.env`. Crea únicamente plantillas `.env.example` con valores ficticios.

---

## 3. Reglas para Modificación y Edición de Archivos

- **Uso de Parches / Diffs:** Al interactuar mediante herramientas de edición, envía parches limpios indicando claramente las líneas a sustituir.
- **Preservación de Formato:** Mantén las sangrías (espacios o tabulaciones), comillas y estilos de código existentes en el proyecto.
- **Comprobación de Sintaxis:** Después de modificar un archivo crítico (código fuente o configuración), ejecuta el linter o el verificador correspondiente si está disponible.

---

## 4. Protocolo de Borrado Seguro

1. **Archivos Protegidos (NUNCA BORRAR):**
   - `.git/`
   - `.ai-project/PROJECT_CONTEXT.md`
   - Archivos de claves o variables reales (`.env`, `.pem`, etc.)
2. **Confirmación Obligatoria:** Si la IA considera necesario eliminar un archivo de código fuente, plantilla o documentación importante, debe solicitar confirmación o verificar que existe una copia en control de versiones (Git).
3. **Limpieza Temp:** Los archivos temporales creados para pruebas (ej: `test_sandbox.*`) deben eliminarse inmediatamente tras completar las pruebas.
