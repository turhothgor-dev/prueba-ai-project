# 📋 PLAN DE IMPLEMENTACIÓN - Mejoras de Error Handling y Pattern Validation

## 🎯 Objetivo

Implementar mejoras de __error handling__ y __validación de patrones en la GUI__ según el roadmap del proyecto (Fase 3 - Mejoras Inmediatas).

---

## 📊 ESTADO ACTUAL (Análisis del Arquitecto)

### ✅ Lo que ya existe:

1. __`src/utils/validators.py`__ - Tiene funciones básicas:

   - `validate_api_key()` - Valida formato de API key
   - `validate_directory()` - Valida ruta de directorio
   - `validate_pattern()` - Valida sintaxis de patrones (NO se usa en la GUI)

2. __`src/gui/config_dialog.py`__ - Tiene validación básica:

   - `_validate_inputs()` - Solo valida API key (longitud mínima)
   - No valida patrones de carpetas/archivos
   - No valida directorio base

3. __`src/core/organizer.py`__ - Manejo de errores básico:

   - Try/except en `organize()` y `preview()`
   - Logging con `logger.error()`
   - Retorna tuplas (success, message)

4. __`src/services/tmdb_service.py`__ - Logging de peticiones:

   - `_log_request()` para debug
   - Manejo de status codes

### ❌ Lo que falta (Roadmap):

1. __Error handling y logging mejorado__ - Centralizado y consistente
2. __Validación de patrones en la GUI__ - En tiempo real con feedback visual
3. __Logging estructurado__ - Niveles, rotación de logs, archivo de logs

---

## 🚀 PLAN PASO A PASO

### __FASE 1: Mejorar Sistema de Logging__ (2-3 pasos)

#### __Paso 1.1: Crear módulo de logging centralizado__

__Archivo:__ `src/utils/logger.py` (NUEVO)

__Objetivo:__ Configurar logging estructurado con rotación de archivos

__Implementación:__

```python
- Crear función setup_logging() que:
  - Configure nivel de logging (DEBUG por defecto)
  - Cree handlers para console (INFO) y archivo (DEBUG)
  - Implemente rotación de logs (RotatingFileHandler, max 5MB, 3 backups)
  - Formato: %(asctime)s - %(name)s - %(levelname)s - %(message)s
  - Retorne logger configurado

- Crear clase LoggingMixin (opcional):
  - Para inyectar logger en clases existentes
```

__Archivos a modificar:__

- `src/main.py` - Llamar a setup_logging() al inicio

---

#### __Paso 1.2: Mejorar logging en TMDB Service__

__Archivo:__ `src/services/tmdb_service.py`

__Cambios:__

```python
- Reemplazar logger = logging.getLogger(__name__) por uso del logger centralizado
- Mejorar _log_request() para:
  - Loggear nivel DEBUG para requests exitosos
  - Loggear nivel WARNING para errores 4xx
  - Loggear nivel ERROR para errores 5xx y excepciones
  - Incluir timestamp, endpoint, params (sin API key), status_code, tiempo de respuesta
```

---

#### __Paso 1.3: Mejorar logging en FileOrganizer__

__Archivo:__ `src/core/organizer.py`

__Cambios:__

```python
- Agregar logging.INFO para operaciones exitosas
- Agregar logging.WARNING para conflictos (archivo ya existe)
- Agregar logging.ERROR para fallos de organización
- Agregar logging.DEBUG para detalles de paths generados
- Capturar y loggear excepciones específicas (FileNotFoundError, PermissionError, etc.)
```

---

### __FASE 2: Validación de Patrones en GUI__ (3-4 pasos)

#### __Paso 2.1: Extender validators.py__

__Archivo:__ `src/utils/validators.py`

__Agregar funciones:__

```python
1. validate_pattern_placeholders(pattern: str, media_type: str = "both") -> tuple[bool, str]
   - Validar que el patrón tenga los placeholders requeridos según tipo
   - Para series: requerir {season} y {episode}
   - Para películas: no requerir season/episode
   - Retornar (True, "") o (False, "mensaje de error")

2. validate_pattern_syntax(pattern: str) -> tuple[bool, str, list[str]]
   - Validación más detallada que validate_pattern() actual
   - Retornar lista de warnings (ej: placeholder opcional no usado)
   - Detectar formatos inválidos (ej: {title:03d} es válido, {title:xyz} no)

3. validate_base_directory(path: str, must_exist: bool = False) -> tuple[bool, str]
   - Mejorar validate_directory() actual
   - Opción para validar directorio que debe existir o puede crearse
   - Validar permisos de escritura
```

---

#### __Paso 2.2: Agregar validación en tiempo real en ConfigDialog__

__Archivo:__ `src/gui/config_dialog.py`

__Cambios en `_init_ui()`:__

```python
1. Agregar labels de validación debajo de cada input:
   - self.folder_pattern_label = QLabel()
   - self.file_pattern_label = QLabel()
   - self.base_dir_label = QLabel()
   - Estilo: color rojo para error, verde para válido, invisible para sin validar

2. Conectar signals de textChanged a métodos de validación:
   - self.folder_pattern_input.textChanged.connect(self._validate_folder_pattern)
   - self.file_pattern_input.textChanged.connect(self._validate_file_pattern)
   - self.base_dir_input.textChanged.connect(self._validate_base_dir)
```

__Nuevos métodos a agregar:__

```python
1. _validate_folder_pattern(text: str) -> None:
   - Llamar a validate_pattern_syntax()
   - Actualizar label con mensaje y color
   - Habilitar/deshabilitar botón de guardar

2. _validate_file_pattern(text: str) -> None:
   - Similar al anterior

3. _validate_base_dir(text: str) -> None:
   - Llamar a validate_base_directory()
   - Validar que el directorio existe o puede crearse

4. _update_save_button_state() -> None:
   - Verificar todos los campos válidos
   - Deshabilitar botón guardar si hay errores críticos
```

---

#### __Paso 2.3: Mejorar validación al guardar__

__Archivo:__ `src/gui/config_dialog.py`

__Modificar `_validate_inputs()`:__

```python
- Validar folder_pattern con validate_pattern_placeholders()
- Validar file_pattern con validate_pattern_placeholders()
- Validar base_directory con validate_base_directory(must_exist=False)
- Retornar warnings específicos para cada campo inválido
- Acumular todos los errores (no solo el primero)
```

__Modificar `_on_save()`:__

```python
- Si hay errores críticos, mostrar QMessageBox con lista de errores
- Si solo hay warnings, mostrar advertencia pero permitir guardar
- Loggear configuración guardada con logging.info()
```

---

#### __Paso 2.4: Agregar tooltips y ayuda contextual__

__Archivo:__ `src/gui/config_dialog.py`

__Agregar:__

```python
1. Tooltips para cada campo:
   - self.folder_pattern_input.setToolTip("Ej: {title} ({year})")
   - self.file_pattern_input.setToolTip("Ej: {title} - S{season:02d}E{episode:02d}")

2. Botón de ayuda "?" junto a cada patrón:
   - Al hacer click, mostrar QDialog con:
     - Lista de placeholders disponibles
     - Ejemplos de uso
     - Previsualización con datos de ejemplo

3. Método _show_pattern_help(pattern_type: str) -> None:
   - Mostrar ayuda contextual según tipo de patrón
```

---

### __FASE 3: Manejo de Errores Mejorado en Organizer__ (2-3 pasos)

#### __Paso 3.1: Crear excepciones personalizadas__

__Archivo:__ `src/core/exceptions.py` (NUEVO)

__Implementación:__

```python
1. class MediaOrganizerError(Exception):
   - Exception base para todas las excepciones del proyecto

2. class MetadataNotFoundError(MediaOrganizerError):
   - Cuando no se encuentran metadatos para un archivo

3. class FileOrganizeError(MediaOrganizerError):
   - Error genérico al organizar archivo
   - Atributos: file_path, reason, original_exception

4. class PatternValidationError(MediaOrganizerError):
   - Error en validación de patrones

5. class CacheError(MediaOrganizerError):
   - Errores de caché

6. class PermissionError(MediaOrganizerError):
   - Sin permisos para escribir en directorio
```

---

#### __Paso 3.2: Refactorizar FileOrganizer para usar excepciones__

__Archivo:__ `src/core/organizer.py`

__Cambios:__

```python
1. Modificar organize() para:
   - Lanzar MetadataNotFoundError si no hay metadatos
   - Lanzar FileOrganizeError con razón específica
   - Mantener retorno de tupla para compatibilidad con GUI

2. Agregar método _validate_before_organize():
   - Validar que archivo existe
   - Validar que hay metadatos
   - Validar que paths son válidos
   - Lanzar excepciones específicas

3. Mejorar manejo de errores en _generate_new_path():
   - Validar que base_directory es accesible
   - Validar que se pueden crear directorios
   - Catch de OSError, PermissionError
```

---

#### __Paso 3.3: Mejorar WorkerThread con manejo de errores__

__Archivo:__ `src/gui/main_window.py`

__Cambios en WorkerThread.run():__

```python
1. Importar excepciones personalizadas
2. Try/except específico por tipo de excepción:
   - MetadataNotFoundError → log warning, continuar con siguiente archivo
   - PermissionError → log error, marcar archivo como fallido
   - FileOrganizeError → log error con detalles
   - Exception genérico → log critical con traceback

3. Agregar traceback completo en logs de errores críticos:
   - import traceback
   - logger.error(f"Error: {e}\n{traceback.format_exc()}")
```

---

### __FASE 4: Tests para las Mejoras__ (2 pasos)

#### __Paso 4.1: Tests para validators mejorados__

__Archivo:__ `tests/test_validators.py` (NUEVO)

__Tests a agregar:__

```python
1. TestValidatePatternPlaceholders:
   - test_valid_movie_pattern
   - test_valid_series_pattern
   - test_missing_season_placeholder
   - test_missing_episode_placeholder
   - test_invalid_placeholder

2. TestValidatePatternSyntax:
   - test_balanced_braces
   - test_format_specifiers
   - test_invalid_format_specifier
   - test_warnings_for_optional_placeholders

3. TestValidateBaseDirectory:
   - test_valid_existing_directory
   - test_valid_new_directory
   - test_invalid_path
   - test_no_write_permissions
```

---

#### __Paso 4.2: Tests para excepciones personalizadas__

__Archivo:__ `tests/test_exceptions.py` (NUEVO)

__Tests a agregar:__

```python
1. TestCustomExceptions:
   - test_metadata_not_found_error
   - test_file_organize_error
   - test_pattern_validation_error
   - test_cache_error
   - test_exception_inheritance
```

---

## 📁 RESUMEN DE ARCHIVOS

### __Archivos Nuevos a Crear:__

1. `src/utils/logger.py` - Logging centralizado
2. `src/core/exceptions.py` - Excepciones personalizadas
3. `tests/test_validators.py` - Tests para validators
4. `tests/test_exceptions.py` - Tests para excepciones

### __Archivos a Modificar:__

1. `src/utils/validators.py` - Agregar funciones de validación
2. `src/gui/config_dialog.py` - Validación en tiempo real + tooltips
3. `src/core/organizer.py` - Logging mejorado + excepciones
4. `src/services/tmdb_service.py` - Logging mejorado
5. `src/gui/main_window.py` - Manejo de errores en WorkerThread
6. `src/main.py` - Inicializar logging

---

## 🎯 CRITERIOS DE ACEPTACIÓN

### __Error Handling:__

- Todas las excepciones logueadas con nivel apropiado
- Logs rotados automáticamente (max 5MB, 3 backups)
- Excepciones personalizadas para errores del dominio
- Traceback completo en logs de errores críticos
- Mensajes de error descriptivos en la GUI

### __Pattern Validation:__

- Validación en tiempo real de patrones (textChanged)
- Feedback visual inmediato (colores rojo/verde)
- Tooltips con ejemplos de uso
- Ayuda contextual con lista de placeholders
- Validación al guardar con lista de errores
- Botón de guardar deshabilitado con errores críticos

### __Tests:__

- 100% de cobertura en validators.py
- Tests para todas las excepciones personalizadas
- Todos los tests existentes continúan pasando (28/28)

---

## 📝 NOTAS PARA EL MODELO PROGRAMADOR

1. __Orden de implementación:__ Seguir las fases en orden (1→2→3→4)
2. __Compatibilidad:__ Mantener compatibilidad con código existente
3. __Tests:__ Ejecutar `pytest` después de cada paso para verificar que no se rompió nada
4. __Logging:__ No loggear información sensible (API keys, paths completos con usernames)
5. __GUI:__ No bloquear el hilo principal con validaciones pesadas
6. __Estilo:__ Mantener convenciones del proyecto (PEP 8, type hints, docstrings)

---

## 🚦 PRÓXIMOS PASOS

Cuando estés listo para comenzar, __cambia a modo Act__ y el modelo programador implementará:

1. __Primero:__ Fase 1 (Logging centralizado) - Paso 1.1
2. __Segundo:__ Fase 2 (Validación en GUI) - Paso 2.1 y 2.2
3. __Tercero:__ Fase 3 (Excepciones) - Paso 3.1
4. __Cuarto:__ Fase 4 (Tests) - Paso 4.1 y 4.2

¿Quieres que proceda con la implementación de la __Fase 1, Paso 1.1__ (crear módulo de logging centralizado)?
