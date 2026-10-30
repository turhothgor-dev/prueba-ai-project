# Guía de Inicio Rápido

## Primeros Pasos

### 1. Obtener API Key de TMDB

1. Ve a [https://www.themoviedb.org/](https://www.themoviedb.org/)
2. Crea una cuenta gratuita
3. Ve a Configuración > API y solicita una API Key
4. Copia tu API Key (v3)

### 2. Instalar la Aplicación

```bash
# Clonar repositorio
git clone <url-del-repositorio>
cd MediaOrganizer

# Crear entorno virtual
python -m venv venv

# Activar entorno
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar

```bash
# Ejecutar la aplicación
python -m src.main
```

1. Haz clic en **Configuración**
2. Introduce tu TMDB API Key
3. Configura el directorio base donde se organizarán los archivos
4. Ajusta los patrones de renombrado si es necesario
5. Haz clic en **Guardar**

### 4. Usar la Aplicación

1. **Añadir Archivos**: Selecciona los archivos de video a organizar
2. **Añadir Carpeta**: Selecciona una carpeta completa para escanear
3. **Revisar**: La aplicación mostrará los metadatos encontrados
4. **Procesar**: Renombra y organiza los archivos según tu configuración

## Patrones de Renombrado

### Para Películas

```
{title} ({year})
```

Ejemplo: `The Matrix (1999).mkv`

### Para Series

```
{title}/Season {season}/{title} - S{season:02d}E{episode:02d}
```

Ejemplo: `Breaking Bad/Season 1/Breaking Bad - S01E01.mkv`

### Placeholders Disponibles

| Placeholder | Descripción | Ejemplo |
|-------------|-------------|---------|
| `{title}` | Título | Breaking Bad |
| `{year}` | Año | 2008 |
| `{season}` | Temporada | 1 |
| `{episode}` | Episodio | 5 |
| `{season:02d}` | Temporada (2 dígitos) | 01 |
| `{episode:02d}` | Episodio (2 dígitos) | 05 |
| `{tmdb_id}` | ID TMDB | 1396 |
| `{imdb_id}` | ID IMDb | tt0903747 |

## Consejos

- **Haz una copia de seguridad** antes de procesar archivos importantes
- **Prueba con pocos archivos** primero para verificar la configuración
- **Usa la vista previa** para confirmar los cambios antes de aplicar
- **La caché** acelera las consultas repetidas (se guarda en `~/.mediaorganizer/cache.db`)

## Solución de Problemas

### La API no responde

- Verifica que tu API Key es correcta
- Comprueba tu conexión a internet
- TMDB tiene límites de tasa (40 solicitudes/10 segundos)

### Los archivos no se renombran correctamente

- Revisa los patrones de renombrado
- Asegúrate de tener permisos de escritura en el directorio
- Verifica que los archivos no estén en uso

### La aplicación se cierra inesperadamente

- Revisa los logs en la consola
- Actualiza las dependencias: `pip install -r requirements.txt --upgrade`
- Reporta el issue en el repositorio
