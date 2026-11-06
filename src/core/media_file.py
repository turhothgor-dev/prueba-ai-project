"""Media file data model and operations."""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MediaFile:
    """Represents a video file with metadata."""

    path: Path
    original_filename: str
    extension: str = ""
    title: str | None = None
    year: int | None = None
    season: int | None = None
    episode: int | None = None
    tmdb_id: int | None = None
    imdb_id: str | None = None
    is_series: bool = False
    metadata_fetched: bool = False

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if not self.extension:
            self.extension = self.path.suffix.lower()
        if not self.original_filename:
            self.original_filename = self.path.name

    @classmethod
    def from_path(cls, file_path: str | Path) -> "MediaFile":
        """Create MediaFile from a file path.

        Args:
            file_path: Path to the video file

        Returns:
            MediaFile instance
        """
        path = Path(file_path)
        return cls(path=path, original_filename=path.name)

    def guess_info_from_filename(self) -> None:
        """Attempt to extract series/movie info from filename."""
        filename = self.path.stem

        # Series pattern: S01E01, 1x01, etc.
        series_patterns = [
            r"[Ss](\d{1,2})[Ee](\d{1,2})",
            r"(\d{1,2})x(\d{1,2})",
            r"[Tt]emp\.?\s*(\d{1,2})\s*[Cc]ap\.?\s*(\d{1,2})",
        ]

        for pattern in series_patterns:
            match = re.search(pattern, filename)
            if match:
                self.is_series = True
                self.season = int(match.group(1))
                self.episode = int(match.group(2))
                break

        # Year pattern
        year_match = re.search(r"\b(19|20)\d{2}\b", filename)
        if year_match:
            self.year = int(year_match.group())

        # Clean title (remove common patterns)
        title = filename
        title = re.sub(r"\b(19|20)\d{2}\b", "", title)
        title = re.sub(r"[\[\](){}]", "", title)
        title = re.sub(r"[Ss]\d{1,2}[Ee]\d{1,2}|\d{1,2}x\d{1,2}", "", title)
        title = re.sub(r"\b(temp|season|cap|episode)\b.*", "", title, flags=re.IGNORECASE)
        title = re.sub(r"\s+", " ", title).strip()
        title = re.sub(r"[\-\._]", " ", title)

        self.title = title.title() if title else None

    def get_new_filename(self, pattern: str) -> str:
        """Generate new filename based on pattern.

        Args:
            pattern: Filename pattern with placeholders

        Returns:
            New filename with extension
        """
        filename = pattern.format(
            title=self.title or "Unknown",
            year=self.year or "Unknown",
            season=self.season or 0,
            episode=self.episode or 0,
        )

        # Sanitize filename
        filename = re.sub(r'[<>:"/\\|?*]', "", filename)
        filename = filename.strip(". ")

        return f"{filename}{self.extension}"

    def exists(self) -> bool:
        """Check if file exists on disk."""
        return self.path.exists()

    def get_size_mb(self) -> float:
        """Get file size in megabytes."""
        if self.exists():
            return self.path.stat().st_size / (1024 * 1024)
        return 0.0
