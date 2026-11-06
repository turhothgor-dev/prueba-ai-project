# 🗺️ Roadmap - MediaOrganizer

> **Última actualización:** 06/11/2026

---

## 📊 Resumen de Estado

| Métrica | Valor |
| --------- | ------- |
| **Versión** | 0.2.0 |
| **Tests Unitarios** | 28/28 passing ✅ |
| **Módulos Core** | 100% implementados |
| **GUI** | Funcional con validación en tiempo real y ayuda contextual |
| **Estado General** | Alpha - En Desarrollo Activo |

---

## ✅ Completado

### Fase 1: Fundamentos

- [x] Estructura inicial del proyecto
- [x] Configuración del entorno (requirements.txt, pyproject.toml)
- [x] Módulo de configuración (JSON-based)
- [x] Modelo de datos MediaFile
- [x] Servicio TMDB API
- [x] Servicio de caché SQLite
- [x] Interfaz GUI básica (MainWindow, ConfigDialog)
- [x] Tests unitarios iniciales (10/10 passing)
- [x] Documentación básica (README, GETTING_STARTED)

### Fase 2: Procesador de Archivos

- [x] **Implementación del procesador de archivos (FileOrganizer)**
- [x] Integración TMDB con el flujo de procesamiento
- [x] Búsqueda automática de metadatos
- [x] Caché local para consultas repetidas
- [x] Renombrado inteligente basado en patrones configurables
- [x] Organización por carpetas (películas y series)
- [x] Manejo de colisiones (reemplazar o saltar)
- [x] Creación automática de directorios
- [x] Tests del organizador (12/12 passing)
- [x] Actualización de GUI con progreso en tiempo real

### Fase 3: Mejoras de UX y Debugging (30/10/2026)

- [x] **API key opcional** (no bloquea guardado de configuración)
- [x] **Toggle 👁/🙈** para mostrar/ocultar API key en configuración
- [x] **Servicios se recargan** automáticamente al guardar config
- [x] **Vista previa de cambios** antes de procesar archivos
- [x] **Mensajes descriptivos** en vista previa (Sin match / Conflicto / Archivo ausente)
- [x] **Eliminar archivos** de la lista (selección múltiple + confirmación)
- [x] **Logging completo** de peticiones TMDB
- [x] **Botón "Logs TMDB"** para abrir logs rápidamente
- [x] Tests: 28/28 passing

### Fase 4: Logging Centralizado (06/11/2026)

- [x] **Módulo de logging centralizado** (`src/utils/logger.py`)
- [x] **Logging con rotación** (5MB, 3 backups)
- [x] **Console handler** (INFO) + **File handler** (DEBUG)
- [x] **Logging mejorado en TMDB Service** (niveles apropiados, timing, excepciones)
- [x] **Logging mejorado en FileOrganizer** (detalle por paso, manejo específico de errores)
- [x] **Inicialización en main.py**

### Fase 5: Validación de Patrones en GUI (06/11/2026)

- [x] **Nuevas funciones en validators.py**
  - [x] `validate_pattern_placeholders()` - Valida placeholders requeridos
  - [x] `validate_pattern_syntax()` - Validación detallada con warnings
  - [x] `validate_base_directory()` - Validación de directorios con permisos
- [x] **Validación en tiempo real en ConfigDialog**
  - [x] Labels con feedback visual (rojo/verde/naranja)
  - [x] Conexión de signals `textChanged`
  - [x] Botón guardar habilitado/deshabilitado según errores
- [x] **Validación mejorada al guardar**
  - [x] Acumulación de todos los errores (no solo el primero)
  - [x] Diálogo de errores críticos bloquea guardado
  - [x] Diálogo de warnings permite guardar
  - [x] Logging de configuración guardada
- [x] **Ayuda contextual**
  - [x] Tooltips con ejemplos en inputs
  - [x] Botones "?" abren dialog de ayuda
  - [x] `PatternHelpDialog` con tabla de placeholders y ejemplos

---

## 🚧 En Progreso

### Mejoras Inmediatas

- [x] **API key de TMDB opcional (no bloquea configuración)**
- [x] **Configuración siempre se guarda (sin pérdida de datos)**
- [x] **Vista previa de cambios antes de aplicar**
- [x] **Manejo de errores y logging mejorado** ✅ COMPLETADO
- [x] **Validación de patrones en la GUI** ✅ COMPLETADO

---

## 📋 Pendiente

### Funcionalidades Futuras

- [ ] **Fase 6: Manejo de Errores con Excepciones Personalizadas**
  - [ ] Crear `src/core/exceptions.py` con excepciones del dominio
  - [ ] Refactorizar FileOrganizer para usar excepciones
  - [ ] Mejorar WorkerThread con manejo específico de excepciones
- [ ] Tests de integración
- [ ] Soporte para IMDb (alternativo a TMDB)
- [ ] Configuración de PyInstaller para builds
- [ ] Empaquetado para distribución
- [ ] Búsqueda y asociación manual de metadatos
- [ ] Historial de operaciones
- [ ] Undo/Redo de cambios
- [ ] Soporte para subtítulos
- [ ] Exportar/importar configuración
- [ ] Internacionalización (i18n)

---

## 📈 Próximos Hitos

| Hito | Descripción | Estado |
| ------ | ------------- | -------- |
| **v0.2.0** | Vista previa + logging + UX mejorada + validación | ✅ Completado |
| **v0.3.0** | Excepciones personalizadas + Tests de integración + IMDb | 🚧 En Progreso |
| **v0.4.0** | Builds con PyInstaller | 📋 Pendiente |
| **v1.0.0** | Versión estable para distribución | 📋 Pendiente |

---

## 🎯 Criterios de Calidad

- **Cobertura de tests:** >80%
- **Tests passing:** 100%
- **Linting:** Ruff + Black
- **Type hints:** Obligatorio en funciones públicas
- **Documentación:** Docstrings en APIs públicas
