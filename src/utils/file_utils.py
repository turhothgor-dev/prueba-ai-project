"""File utility functions."""

import re
from pathlib import Path
from typing import List


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for all platforms
    """
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "", filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(". ")

    # Limit length (255 is typical max for most filesystems)
    if len(sanitized) > 255:
        name, ext = Path(sanitized).stem, Path(sanitized).suffix
        sanitized = name[: 255 - len(ext)] + ext

    return sanitized


def get_video_files(directory: str | Path, recursive: bool = True) -> List[Path]:
    """Get all video files from a directory.

    Args:
        directory: Directory path to search
        recursive: Whether to search subdirectories

    Returns:
        List of Path objects for video files
    """
    video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"}
    path = Path(directory)

    if recursive:
        files = [f for f in path.rglob("*") if f.suffix.lower() in video_extensions]
    else:
        files = [f for f in path.glob("*") if f.suffix.lower() in video_extensions]

    return sorted(files)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def ensure_directory(path: str | Path) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
