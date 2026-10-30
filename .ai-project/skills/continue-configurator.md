# ⚙️ Skill: continue-configurator

## Objetivo
Mantener sincronizados los modelos, endpoints y roles del archivo `.continue/config.yaml` con las variables de entorno del proyecto.

## Protocolo de Ejecución
1. Validar la existencia de `.continue/config.yaml` y `.env`.
2. Reemplazar dinámicamente las variables `${OS_ARCHITECT_MODEL}`, `${OS_CODER_MODEL}` y `${OPENAI_COMPATIBLE_ENDPOINT}` según el proveedor seleccionado (Ollama, LM Studio, vLLM u OpenRouter).
3. Asegurar que los roles `chat`, `edit` y `autocomplete` estén asignados a los modelos con el tamaño y la especialización adecuados.

