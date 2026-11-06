# MediaOrganizer

Aplicación de escritorio para organizar y renombrar archivos de video usando metadatos de TMDB/IMDb.

## 🚀 Características

- **Búsqueda automática de metadatos** desde TMDB
- **Renombrado inteligente** de archivos de video
- **Organización por carpetas** según serie/película
- **Caché local** para consultas repetidas
- **Interfaz gráfica** moderna con PyQt6
- **Multiplataforma** (Windows, macOS, Linux)

## 📋 Requisitos

- Python 3.11+
- PyQt6
- TMDB API Key (gratuita en <https://www.themoviedb.org/settings/api>)

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd MediaOrganizer
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar API Key

Ejecuta la aplicación y ve a Configuración > API para introducir tu TMDB API Key.

## 💻 Uso

### Ejecutar la aplicación

```bash
python -m src.main
```

### Flujo de trabajo

1. **Añadir archivos**: Selecciona archivos o carpetas con videos
2. **Revisar metadatos**: La aplicación busca automáticamente la información
3. **Configurar patrones**: Define cómo quieres organizar los archivos
4. **Procesar**: La aplicación renombra y organiza los archivos

## 📁 Estructura del Proyecto

```text
MediaOrganizer/
├── src/
│   ├── core/           # Lógica de negocio y modelos
│   ├── gui/            # Interfaz gráfica PyQt6
│   ├── services/       # Servicios externos (API, caché)
│   ├── utils/          # Funciones utilitarias
│   └── main.py         # Punto de entrada
├── tests/              # Tests unitarios
├── docs/               # Documentación
├── assets/             # Recursos (iconos, imágenes)
├── requirements.txt    # Dependencias
└── README.md
```

## 🧪 Tests

```bash
pytest
```

## 📦 Generar ejecutable

### Windows

```bash
pyinstaller --name="MediaOrganizer" --windowed --onefile src/main.py
```

### macOS

```bash
pyinstaller --name="MediaOrganizer" --windowed --onefile src/main.py
```

### Linux

```bash
pyinstaller --name="MediaOrganizer" --windowed --onefile src/main.py
```

## 📝 Configuración

La configuración se guarda en `~/.mediaorganizer/config.json`

### Patrones disponibles

Season y Episode solo tendrá sentido en series, no en películas.

| Placeholder | Descripción |
| ------------- | ------------- |
| `{title}` | Título de la película/serie |
| `{year}` | Año de lanzamiento |
| `{season}` | Número de temporada |
| `{episode}` | Número de episodio |
| `{tmdb_id}` | ID de TMDB |
| `{imdb_id}` | ID de IMDb |

### Ejemplos de patrones

- **Películas**: `{title} - ({year}) - [tmdbid-{tmdb_id}]`
- **Series**: `{title}/Season {season}/{title} - S{season:02d}E{episode:02d} - [tmdbid-{tmdb_id}]`

## Estado del desarrollo

Para el estado actual, tareas completadas y plan de desarrollo, consultar:
📄 **[.ai-project/ROADMAP.md](.ai-project/ROADMAP.md)**

## AI Project Context

Directrices para los modelos de IA, consultar:
📄 **[.ai-project/PROJECT_CONTEXT.md](.ai-project/PROJECT_CONTEXT.md)**

## 🤝 Contribuir[tmdbid-{tmdb_id}][tmdbid-{[tmdbid-{tmdb_id}]tmdb_id}]

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

## 🙏 Agradecimientos

- [TMDB](https://www.themoviedb.org/) por su API gratuita
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) por el framework GUI
