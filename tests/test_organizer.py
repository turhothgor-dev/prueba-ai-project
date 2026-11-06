"""Tests for FileOrganizer class."""

from unittest.mock import MagicMock

import pytest

from src.core.config import Config
from src.core.media_file import MediaFile
from src.core.organizer import FileOrganizer
from src.services.cache_service import CacheService
from src.services.tmdb_service import TMDBService


class TestFileOrganizer:
    """Test cases for FileOrganizer class."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing."""
        return tmp_path / "media"

    @pytest.fixture
    def config(self, tmp_path):
        """Create a test configuration."""
        config_file = tmp_path / "config.json"
        config = Config(config_file)
        config.set("organization.base_directory", str(tmp_path / "organized"))
        config.set("organization.folder_pattern", "{title} ({year})")
        config.set("organization.file_pattern", "{title} - S{season:02d}E{episode:02d}")
        config.set("organization.create_season_folders", True)
        config.set("organization.replace_existing", False)
        return config

    @pytest.fixture
    def mock_tmdb_service(self):
        """Create a mock TMDB service."""
        service = MagicMock(spec=TMDBService)
        service.search = MagicMock(return_value=[])
        service.get_episode_details = MagicMock(return_value={})
        return service

    @pytest.fixture
    def cache_service(self, tmp_path):
        """Create a cache service for testing."""
        cache_path = tmp_path / "test_cache.db"
        return CacheService(db_path=cache_path)

    @pytest.fixture
    def organizer(self, config, mock_tmdb_service, cache_service):
        """Create a FileOrganizer instance."""
        return FileOrganizer(
            config=config,
            cache_service=cache_service,
            tmdb_service=mock_tmdb_service,
        )

    def test_organize_movie(self, config, mock_tmdb_service, cache_service, temp_dir):
        """Test organizing a movie file."""
        # Create organizer with movie pattern
        config.set("organization.file_pattern", "{title} ({year})")
        organizer = FileOrganizer(
            config=config,
            cache_service=cache_service,
            tmdb_service=mock_tmdb_service,
        )

        # Create a test movie file
        test_file = temp_dir / "test.movie.2024.mkv"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()

        # Create MediaFile
        media_file = MediaFile.from_path(test_file)
        media_file.title = "Test Movie"
        media_file.year = 2024
        media_file.metadata_fetched = True

        # Organize
        success, message = organizer.organize(media_file)

        assert success is True
        assert "Organizado" in message
        assert media_file.original_filename == "Test Movie (2024).mkv"

    def test_organize_series(self, organizer, temp_dir):
        """Test organizing a TV series file."""
        # Create a test series file
        test_file = temp_dir / "test.show.s01e05.mkv"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()

        # Create MediaFile
        media_file = MediaFile.from_path(test_file)
        media_file.guess_info_from_filename()
        media_file.title = "Test Show"
        media_file.year = 2023
        media_file.metadata_fetched = True

        # Organize
        success, message = organizer.organize(media_file)

        assert success is True
        assert "Organizado" in message
        assert media_file.is_series is True
        assert media_file.season == 1
        assert media_file.episode == 5

    def test_organize_file_not_found(self, organizer):
        """Test organizing a file that doesn't exist."""
        # Create MediaFile for non-existent file
        media_file = MediaFile.from_path("/nonexistent/file.mkv")
        media_file.title = "Nonexistent"
        media_file.year = 2024
        media_file.metadata_fetched = True

        # Organize
        success, message = organizer.organize(media_file)

        assert success is False
        assert "no existe" in message.lower()

    def test_organize_no_metadata(self, organizer, temp_dir):
        """Test organizing without metadata."""
        # Create a test file
        test_file = temp_dir / "test.mkv"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()

        # Create MediaFile without metadata
        media_file = MediaFile.from_path(test_file)

        # Mock TMDB to return no results
        organizer.tmdb.search = MagicMock(return_value=[])

        # Organize
        success, message = organizer.organize(media_file)

        assert success is False
        assert "metadatos" in message.lower()

    def test_organize_replace_existing(self, organizer, temp_dir):
        """Test organizing with replace_existing enabled."""
        # Enable replace
        organizer.replace_existing = True

        # Create destination directory and file
        dest_dir = temp_dir / "Test (2024)"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / "Test (2024).mkv"
        dest_file.touch()

        # Create source file
        source_file = temp_dir / "source.mkv"
        source_file.touch()

        # Create MediaFile
        media_file = MediaFile.from_path(source_file)
        media_file.title = "Test"
        media_file.year = 2024
        media_file.metadata_fetched = True

        # Organize
        success, message = organizer.organize(media_file)

        assert success is True

    def test_organize_conflict_without_replace(self, tmp_path):
        """Test organizing with conflict when replace is disabled."""
        # Create temp directory
        temp_dir = tmp_path / "media"
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Create config directory and file
        config_dir = temp_dir / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.json"
        config = Config(config_file)
        config.set("organization.base_directory", str(temp_dir))
        config.set("organization.folder_pattern", "{title} ({year})")
        config.set("organization.file_pattern", "{title} ({year})")
        config.set("organization.create_season_folders", False)
        config.set("organization.replace_existing", False)

        # Create mock services
        mock_tmdb = MagicMock(spec=TMDBService)
        mock_tmdb.search = MagicMock(return_value=[])
        mock_tmdb.get_episode_details = MagicMock(return_value={})
        cache = CacheService(db_path=temp_dir / "cache.db")

        organizer = FileOrganizer(
            config=config,
            cache_service=cache,
            tmdb_service=mock_tmdb,
        )

        # Create destination directory and file
        dest_dir = temp_dir / "Test (2024)"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / "Test (2024).mkv"
        dest_file.touch()

        # Create source file
        source_file = temp_dir / "source.mkv"
        source_file.touch()

        # Create MediaFile
        media_file = MediaFile.from_path(source_file)
        media_file.title = "Test"
        media_file.year = 2024
        media_file.metadata_fetched = True

        # Organize
        success, message = organizer.organize(media_file)

        assert success is False
        assert "ya existe" in message.lower()

    def test_generate_new_path_movie(self, organizer):
        """Test generating new path for a movie."""
        media_file = MediaFile.from_path("/test/movie.mkv")
        media_file.title = "Test Movie"
        media_file.year = 2024

        path = organizer._generate_new_path(media_file)

        assert "Test Movie (2024)" in str(path)
        assert path.suffix == ".mkv"

    def test_generate_new_path_series(self, organizer):
        """Test generating new path for a TV series."""
        media_file = MediaFile.from_path("/test/show.mkv")
        media_file.title = "Test Show"
        media_file.year = 2023
        media_file.is_series = True
        media_file.season = 2
        media_file.episode = 5

        path = organizer._generate_new_path(media_file)

        assert "Test Show (2023)" in str(path)
        assert "Season 2" in str(path)
        assert "S02E05" in path.name

    def test_fetch_metadata_from_cache(self, organizer):
        """Test fetching metadata from cache."""
        # Add something to cache
        cache_key = "tmdb_Test_Movie"
        cached_data = {
            "title": "Test Movie",
            "year": 2024,
            "tmdb_id": 12345,
            "media_type": "movie",
        }
        organizer.cache.set(cache_key, cached_data, ttl_days=7)

        # Create MediaFile
        media_file = MediaFile.from_path("/test/movie.mkv")
        media_file.title = "Test Movie"

        # Fetch metadata
        result = organizer._fetch_metadata(media_file)

        assert result is True
        assert media_file.title == "Test Movie"
        assert media_file.year == 2024

    def test_fetch_metadata_from_tmdb(self, organizer):
        """Test fetching metadata from TMDB API."""
        # Create a proper result object (not MagicMock for __dict__ to work)
        from src.services.tmdb_service import TMDBSearchResult

        mock_result = TMDBSearchResult(
            tmdb_id=12345,
            title="TMDB Movie",
            original_title="TMDB Movie",
            year=2024,
            media_type="movie",
        )
        organizer.tmdb.search = MagicMock(return_value=[mock_result])

        # Create MediaFile
        media_file = MediaFile.from_path("/test/movie.mkv")
        media_file.title = "TMDB Movie"

        # Fetch metadata
        result = organizer._fetch_metadata(media_file)

        assert result is True
        assert media_file.title == "TMDB Movie"
        assert media_file.tmdb_id == 12345

    def test_fetch_metadata_no_results(self, organizer):
        """Test fetching metadata when no results are found."""
        # Mock empty TMDB response
        organizer.tmdb.search = MagicMock(return_value=[])

        # Create MediaFile
        media_file = MediaFile.from_path("/test/movie.mkv")
        media_file.title = "Nonexistent Movie"

        # Fetch metadata
        result = organizer._fetch_metadata(media_file)

        assert result is False

    def test_no_base_directory(self, config, mock_tmdb_service, cache_service, tmp_path):
        """Test organizing without a base directory configured."""
        # Remove base directory
        config.set("organization.base_directory", "")

        organizer = FileOrganizer(
            config=config,
            cache_service=cache_service,
            tmdb_service=mock_tmdb_service,
        )

        # Create temp directory and test file
        temp_dir = tmp_path / "media"
        temp_dir.mkdir(parents=True, exist_ok=True)
        test_file = temp_dir / "test.mkv"
        test_file.touch()

        # Create MediaFile
        media_file = MediaFile.from_path(test_file)
        media_file.title = "Test"
        media_file.year = 2024
        media_file.metadata_fetched = True

        # Organize
        success, message = organizer.organize(media_file)

        assert success is True

    # === Tests para Preview ===

    def test_preview_movie(self, config, mock_tmdb_service, cache_service, temp_dir):
        """Test preview for a movie file."""
        config.set("organization.file_pattern", "{title} ({year})")
        organizer = FileOrganizer(
            config=config,
            cache_service=cache_service,
            tmdb_service=mock_tmdb_service,
        )

        # Create test file
        test_file = temp_dir / "test.movie.2024.mkv"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()

        # Create MediaFile
        media_file = MediaFile.from_path(test_file)
        media_file.title = "Test Movie"
        media_file.year = 2024
        media_file.metadata_fetched = True

        # Preview
        success, new_filename, new_path = organizer.preview(media_file)

        assert success is True
        assert "Test Movie (2024)" in new_filename
        assert new_path.endswith(".mkv")

    def test_preview_series(self, config, mock_tmdb_service, cache_service, temp_dir):
        """Test preview for a TV series file."""
        config.set("organization.file_pattern", "{title} - S{season:02d}E{episode:02d}")
        organizer = FileOrganizer(
            config=config,
            cache_service=cache_service,
            tmdb_service=mock_tmdb_service,
        )

        # Create test file
        test_file = temp_dir / "test.show.s01e05.mkv"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()

        # Create MediaFile
        media_file = MediaFile.from_path(test_file)
        media_file.guess_info_from_filename()
        media_file.title = "Test Show"
        media_file.year = 2023
        media_file.metadata_fetched = True

        # Preview
        success, new_filename, new_path = organizer.preview(media_file)

        assert success is True
        assert "Test Show (2023)" in new_path
        assert "S01E05" in new_filename

    def test_preview_no_metadata(self, config, mock_tmdb_service, cache_service, temp_dir):
        """Test preview when no metadata can be found."""
        organizer = FileOrganizer(
            config=config,
            cache_service=cache_service,
            tmdb_service=mock_tmdb_service,
        )

        # Mock TMDB to return no results
        organizer.tmdb.search = MagicMock(return_value=[])

        # Create test file
        test_file = temp_dir / "unknown.file.mkv"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()

        # Create MediaFile without metadata
        media_file = MediaFile.from_path(test_file)

        # Preview
        success, new_filename, new_path = organizer.preview(media_file)

        assert success is False
        assert "metadatos" in new_path.lower()

    def test_preview_file_not_found(self, config, mock_tmdb_service, cache_service):
        """Test preview for a file that doesn't exist."""
        organizer = FileOrganizer(
            config=config,
            cache_service=cache_service,
            tmdb_service=mock_tmdb_service,
        )

        # Create MediaFile for non-existent file
        media_file = MediaFile.from_path("/nonexistent/file.mkv")
        media_file.title = "Nonexistent"
        media_file.year = 2024
        media_file.metadata_fetched = True

        # Preview
        success, new_filename, new_path = organizer.preview(media_file)

        assert success is False
        assert "no existe" in new_path.lower()

    def test_preview_conflict(self, config, mock_tmdb_service, cache_service, tmp_path):
        """Test preview when destination file already exists."""
        temp_dir = tmp_path / "media"
        temp_dir.mkdir(parents=True, exist_ok=True)

        config_file = temp_dir / "config.json"
        config_dir = temp_dir / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        config = Config(config_file)
        config.set("organization.base_directory", str(temp_dir))
        config.set("organization.replace_existing", False)
        config.set("organization.file_pattern", "{title} ({year})")
        config.set("organization.folder_pattern", "{title} ({year})")
        config.set("organization.create_season_folders", False)

        organizer = FileOrganizer(
            config=config,
            cache_service=CacheService(db_path=temp_dir / "cache.db"),
            tmdb_service=MagicMock(spec=TMDBService),
        )

        # Create destination file
        dest_dir = temp_dir / "Test (2024)"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / "Test (2024).mkv"
        dest_file.touch()

        # Create source file
        source_file = temp_dir / "source.mkv"
        source_file.touch()

        # Create MediaFile
        media_file = MediaFile.from_path(source_file)
        media_file.title = "Test"
        media_file.year = 2024
        media_file.metadata_fetched = True

        # Preview
        success, new_filename, new_path = organizer.preview(media_file)

        assert success is False
        assert "Conflicto" in new_path or "ya existe" in new_path

    def test_preview_replace_enabled(self, config, mock_tmdb_service, cache_service, temp_dir):
        """Test preview with replace_existing enabled."""
        config.set("organization.replace_existing", True)
        config.set("organization.file_pattern", "{title} ({year})")
        organizer = FileOrganizer(
            config=config,
            cache_service=cache_service,
            tmdb_service=mock_tmdb_service,
        )

        # Create destination file
        dest_dir = temp_dir / "organized" / "Test (2024)"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / "Test (2024).mkv"
        dest_file.touch()

        # Create source file
        source_file = temp_dir / "source.mkv"
        source_file.touch()

        # Create MediaFile
        media_file = MediaFile.from_path(source_file)
        media_file.title = "Test"
        media_file.year = 2024
        media_file.metadata_fetched = True

        # Preview
        success, new_filename, new_path = organizer.preview(media_file)

        assert success is True  # Should succeed because replace is enabled
