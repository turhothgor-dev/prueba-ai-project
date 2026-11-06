"""Tests for MediaFile class."""

from src.core.media_file import MediaFile


class TestMediaFile:
    """Test cases for MediaFile data model."""

    def test_from_path(self, tmp_path):
        """Test creating MediaFile from path."""
        test_file = tmp_path / "test_video.mp4"
        test_file.touch()

        media = MediaFile.from_path(test_file)

        assert media.path == test_file
        assert media.original_filename == "test_video.mp4"
        assert media.extension == ".mp4"

    def test_guess_info_movie_filename(self):
        """Test extracting info from movie filename."""
        media = MediaFile.from_path("/videos/The Matrix (1999).mkv")
        media.guess_info_from_filename()

        assert media.title == "The Matrix"
        assert media.year == 1999
        assert media.is_series is False

    def test_guess_info_series_filename(self):
        """Test extracting info from series filename."""
        media = MediaFile.from_path("/videos/Show.Name.S01E05.720p.mkv")
        media.guess_info_from_filename()

        assert media.is_series is True
        assert media.season == 1
        assert media.episode == 5

    def test_get_new_filename(self):
        """Test generating new filename from pattern."""
        media = MediaFile.from_path("/videos/old_name.avi")
        media.title = "New Title"
        media.year = 2024
        media.season = 1
        media.episode = 5

        pattern = "{title} ({year}) - S{season:02d}E{episode:02d}"
        new_name = media.get_new_filename(pattern)

        assert new_name == "New Title (2024) - S01E05.avi"

    def test_exists(self, tmp_path):
        """Test file existence check."""
        existing = tmp_path / "exists.mp4"
        existing.touch()

        media_existing = MediaFile.from_path(existing)
        media_nonexisting = MediaFile.from_path(tmp_path / "not_exists.mp4")

        assert media_existing.exists() is True
        assert media_nonexisting.exists() is False
