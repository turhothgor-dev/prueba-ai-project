# 🗺️ Roadmap - MediaOrganizer

> **Última actualización:** 30/10/2026

---

## 📊 Resumen de Estado

| Métrica | Valor |
| --------- | ------- |
| **Versión** | 0.1.0 |
| **Tests Unitarios** | 28/28 passing ✅ |
| **Módulos Core** | 100% implementados |
| **GUI** | Funcional con vista previa |
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

---

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

---

## 🚧 En Progreso

### Mejoras Inmediatas

- [x] **API key de TMDB opcional (no bloquea configuración)**
- [x] **Configuración siempre se guarda (sin pérdida de datos)**
- [x] **Vista previa de cambios antes de aplicar**
- [ ] Manejo de errores y logging mejorado
- [ ] Validación de patrones en la GUI

---

## 📋 Pendiente

### Funcionalidades Futuras

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
| **v0.2.0** | Vista previa + logging + UX mejorada | ✅ Completado |
| **v0.3.0** | Tests de integración + IMDb | 📋 Pendiente |
| **v0.4.0** | Builds con PyInstaller | 📋 Pendiente |
| **v1.0.0** | Versión estable para distribución | 📋 Pendiente |

---

## 🎯 Criterios de Calidad

- **Cobertura de tests:** >80%
- **Tests passing:** 100%
- **Linting:** Ruff + Black
- **Type hints:** Obligatorio en funciones públicas
- **Documentación:** Docstrings en APIs públicas
