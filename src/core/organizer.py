"""File organizer module - handles renaming and moving media files."""

from pathlib import Path

from src.core.config import Config
from src.core.media_file import MediaFile
from src.services.cache_service import CacheService
from src.services.tmdb_service import TMDBService
from src.utils.file_utils import ensure_directory, sanitize_filename
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FileOrganizer:
    """Organizes media files by renaming and moving them based on metadata."""

    def __init__(
        self,
        config: Config,
        cache_service: CacheService,
        tmdb_service: TMDBService,
    ) -> None:
        """Initialize the file organizer.

        Args:
            config: Application configuration
            cache_service: Cache service for storing API responses
            tmdb_service: TMDB API service for fetching metadata
        """
        self.config = config
        self.cache = cache_service
        self.tmdb = tmdb_service
        self.base_directory = Path(config.get("organization.base_directory", ""))
        self.folder_pattern = config.get("organization.folder_pattern", "{title} ({year})")
        self.file_pattern = config.get(
            "organization.file_pattern", "{title} - S{season:02d}E{episode:02d}"
        )
        self.create_season_folders = config.get("organization.create_season_folders", True)
        self.replace_existing = config.get("organization.replace_existing", False)

    def organize(self, media_file: MediaFile) -> tuple[bool, str]:
        """Organize a single media file.

        This method will:
        1. Try to fetch metadata from TMDB if not already available
        2. Generate new filename based on configured patterns
        3. Move/rename the file to the correct location

        Args:
            media_file: The MediaFile to organize

        Returns:
            Tuple of (success: bool, message: str)
        """
        logger.info("Organizing file: %s", media_file.original_filename)

        try:
            # Step 1: Ensure we have metadata
            if not media_file.metadata_fetched:
                logger.debug("Fetching metadata for: %s", media_file.original_filename)
                if not self._fetch_metadata(media_file):
                    logger.warning(
                        "No metadata found for: %s", media_file.original_filename
                    )
                    return (
                        False,
                        f"No se encontraron metadatos para '{media_file.original_filename}'",
                    )
                media_file.metadata_fetched = True
                logger.info(
                    "Metadata fetched: %s (%s)",
                    media_file.title,
                    media_file.year or "unknown year",
                )

            # Step 2: Generate new paths
            new_path = self._generate_new_path(media_file)
            logger.debug(
                "Generated path: %s -> %s",
                media_file.path,
                new_path,
            )

            # Step 3: Check for conflicts
            if new_path.exists() and not self.replace_existing:
                logger.warning(
                    "File conflict: %s already exists (replace=%s)",
                    new_path.name,
                    self.replace_existing,
                )
                return (
                    False,
                    f"El archivo ya existe: {new_path.name}",
                )

            # Step 4: Move/rename the file
            if not media_file.exists():
                logger.error(
                    "Source file not found: %s", media_file.path
                )
                return (
                    False,
                    f"El archivo original no existe: {media_file.path}",
                )

            # Ensure destination directory exists
            try:
                ensure_directory(new_path.parent)
            except OSError as e:
                logger.error(
                    "Failed to create directory %s: %s", new_path.parent, e
                )
                return False, f"Error creando directorio: {e}"

            # Move the file
            try:
                new_path_resolved = new_path.resolve()
                media_file.path = new_path_resolved
                media_file.original_filename = new_path_resolved.name
                logger.info(
                    "Organized: %s -> %s",
                    media_file.path.parent / media_file.original_filename,
                    new_path_resolved,
                )
            except PermissionError as e:
                logger.error(
                    "Permission denied moving file: %s -> %s | %s",
                    media_file.path,
                    new_path,
                    e,
                )
                return False, f"Permiso denegado: {e}"
            except OSError as e:
                logger.error(
                    "OS error moving file: %s -> %s | %s",
                    media_file.path,
                    new_path,
                    e,
                )
                return False, f"Error moviendo archivo: {e}"

            return True, f"Organizado: {new_path_resolved.name}"

        except FileNotFoundError as e:
            logger.error("File not found during organization: %s | %s", media_file.path, e)
            return False, f"Archivo no encontrado: {e}"
        except PermissionError as e:
            logger.error("Permission error during organization: %s | %s", media_file.path, e)
            return False, f"Permiso denegado: {e}"
        except Exception as e:
            logger.error(
                "Unexpected error organizing %s: %s | %s",
                media_file.path,
                e,
                type(e).__name__,
                exc_info=True,
            )
            return False, f"Error inesperado: {str(e)}"

    def _fetch_metadata(self, media_file: MediaFile) -> bool:
        """Fetch metadata from TMDB for a media file.

        Args:
            media_file: The MediaFile to fetch metadata for

        Returns:
            True if metadata was successfully fetched, False otherwise
        """
        # Extract search terms from filename
        search_query = media_file.title or media_file.path.stem

        if not search_query:
            logger.warning("No search query available for: %s", media_file.path)
            return False

        # Try to use cached results first
        cache_key = f"tmdb_{search_query.replace(' ', '_')}"
        cached = self.cache.get(cache_key)

        if cached:
            logger.info("Using cache for: %s", search_query)
            self._apply_metadata(media_file, cached)
            if media_file.title:
                logger.debug(
                    "Metadata from cache: %s (%s)",
                    media_file.title,
                    media_file.year or "unknown",
                )
                return True
            return False

        # Search TMDB
        logger.debug("Searching TMDB for: %s (year=%s)", search_query, media_file.year)

        try:
            results = self.tmdb.search(query=search_query, year=media_file.year)

            if not results:
                logger.warning("No TMDB results for: %s", search_query)
                return False

            # Use the first result (could be improved with user selection)
            best_match = results[0]
            media_file.tmdb_id = best_match.tmdb_id
            media_file.title = best_match.title
            media_file.year = best_match.year

            logger.info(
                "TMDB match: %s (%s) [type=%s, id=%d]",
                best_match.title,
                best_match.year,
                best_match.media_type,
                best_match.tmdb_id,
            )

            # Cache the result (filter non-serializable attributes)
            cache_data = {
                k: v
                for k, v in best_match.__dict__.items()
                if isinstance(v, (str, int, float, bool, type(None)))
            }
            self.cache.set(cache_key, cache_data)
            logger.debug("Cached metadata for: %s", search_query)

            # If it's a TV show, try to get season/episode info
            if best_match.media_type == "tv" and media_file.is_series:
                logger.debug(
                    "Fetching TV episode info: S%dE%d for show %s",
                    media_file.season or "?",
                    media_file.episode or "?",
                    media_file.title,
                )
                self._fetch_tv_episode_info(media_file)

            return True

        except Exception as e:
            logger.error(
                "Error fetching TMDB metadata for '%s': %s | %s",
                search_query,
                e,
                type(e).__name__,
                exc_info=True,
            )
            return False

    def _fetch_tv_episode_info(self, media_file: MediaFile) -> None:
        """Fetch detailed episode information from TMDB for TV shows.

        Args:
            media_file: The MediaFile with TV show info
        """
        if not media_file.tmdb_id or not media_file.season or not media_file.episode:
            logger.debug(
                "Skipping TV episode info: missing tmdb_id=%s, season=%s, episode=%s",
                media_file.tmdb_id,
                media_file.season,
                media_file.episode,
            )
            return

        try:
            logger.debug(
                "Fetching episode details: S%dE%d for TV show %s (ID=%d)",
                media_file.season,
                media_file.episode,
                media_file.title,
                media_file.tmdb_id,
            )
            episode_details = self.tmdb.get_episode_details(
                tv_id=media_file.tmdb_id,
                season=media_file.season,
                episode=media_file.episode,
            )

            if episode_details:
                # Update title with episode title if available
                episode_title = episode_details.get("name")
                if episode_title:
                    media_file.title = f"{media_file.title} - {episode_title}"
                    logger.debug(
                        "Episode title updated: %s", media_file.title
                    )
                else:
                    logger.debug("No episode title found for S%dE%d", media_file.season, media_file.episode)
            else:
                logger.warning(
                    "No episode details returned for S%dE%d of show %s",
                    media_file.season,
                    media_file.episode,
                    media_file.title,
                )
        except Exception as e:
            logger.error(
                "Error fetching episode details S%dE%d for %s: %s | %s",
                media_file.season,
                media_file.episode,
                media_file.title,
                e,
                type(e).__name__,
                exc_info=True,
            )

    def _apply_metadata(self, media_file: MediaFile, metadata: dict) -> None:
        """Apply cached metadata to a media file.

        Args:
            media_file: The MediaFile to update
            metadata: Cached metadata dictionary
        """
        if "title" in metadata:
            media_file.title = metadata["title"]
        if "year" in metadata:
            media_file.year = metadata["year"]
        if "tmdb_id" in metadata:
            media_file.tmdb_id = metadata["tmdb_id"]
        if "media_type" in metadata:
            media_file.is_series = metadata["media_type"] == "tv"

    def _generate_new_path(self, media_file: MediaFile) -> Path:
        """Generate the new file path based on configuration.

        Args:
            media_file: The MediaFile to generate path for

        Returns:
            Path object for the new location
        """
        # Generate filename
        filename = media_file.get_new_filename(self.file_pattern)

        # Generate directory path
        if media_file.is_series and self.create_season_folders:
            # TV show structure: Base/Show Name/Season X/
            season_num = media_file.season or 1
            dir_pattern = f"{self.folder_pattern}/Season {season_num}"
            dir_name = dir_pattern.format(
                title=media_file.title or "Unknown",
                year=media_file.year or "Unknown",
                season=season_num,
            )
        else:
            # Movie structure: Base/Movie Name (Year)/
            dir_name = self.folder_pattern.format(
                title=media_file.title or "Unknown",
                year=media_file.year or "Unknown",
            )

        # Sanitize directory name
        dir_name = sanitize_filename(dir_name)

        # Combine base directory with path components
        if self.base_directory:
            return self.base_directory / dir_name / filename
        else:
            # If no base directory, use the file's current directory
            return media_file.path.parent / dir_name / filename

    def preview(self, media_file: MediaFile) -> tuple[bool, str, str]:
        """Preview the changes for a media file without moving it.

        This method simulates the organization process and returns
        what would happen without actually moving any files.

        Args:
            media_file: The MediaFile to preview

        Returns:
            Tuple of (success, new_filename, new_path)
            - success: True if the file would be organized successfully
            - new_filename: The new filename that would be used
            - new_path: The full destination path
        """
        logger.info("Preview for file: %s", media_file.original_filename)

        try:
            # Step 1: Ensure we have metadata
            if not media_file.metadata_fetched:
                logger.debug("Fetching metadata for preview: %s", media_file.original_filename)
                if not self._fetch_metadata(media_file):
                    logger.warning(
                        "Preview failed: no metadata for %s",
                        media_file.original_filename,
                    )
                    return (
                        False,
                        media_file.original_filename,
                        f"No se encontraron metadatos para '{media_file.original_filename}'",
                    )
                media_file.metadata_fetched = True

            # Step 2: Generate new path
            new_path = self._generate_new_path(media_file)
            new_filename = new_path.name
            logger.debug("Preview path: %s", new_path)

            # Step 3: Check for conflicts
            if new_path.exists() and not self.replace_existing:
                logger.warning(
                    "Preview conflict: %s already exists",
                    new_path,
                )
                return (
                    False,
                    new_filename,
                    "Conflicto: el archivo ya existe en destino",
                )

            # Step 4: Check source file exists
            if not media_file.exists():
                logger.error(
                    "Preview failed: source file not found: %s", media_file.path
                )
                return (
                    False,
                    new_filename,
                    f"El archivo original no existe: {media_file.path}",
                )

            logger.info(
                "Preview OK: %s -> %s",
                media_file.original_filename,
                new_filename,
            )
            return True, new_filename, str(new_path)

        except FileNotFoundError as e:
            logger.error("Preview file not found: %s | %s", media_file.path, e)
            return False, media_file.original_filename, f"Archivo no encontrado: {e}"
        except Exception as e:
            logger.error(
                "Unexpected error in preview of %s: %s | %s",
                media_file.path,
                e,
                type(e).__name__,
                exc_info=True,
            )
            return False, media_file.original_filename, f"Error: {str(e)}"
