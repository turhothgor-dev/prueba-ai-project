# 📂 Skill: file-system-manager

## Objetivo
Regir la lectura, modificación por parches (diffs), creación y eliminación de ficheros del workspace.

## Protocolo de Ejecución
1. Consultar el protocolo detallado en `.ai-project/docs/AI_FILE_OPERATIONS.md`.
2. **Edición:** Priorizar modificaciones de líneas específicas (parches mínimos viables) sobre la reescritura total de ficheros largos.
3. **Ficheros Protegidos:** Queda estrictamente prohibida la edición o borrado automático de `.git/`, `.env` y archivos centrales de `.ai-project/`.
4. **Limpieza:** Borrar automáticamente cualquier script o archivo temporal creado durante la fase de pruebas al concluir la tarea.

