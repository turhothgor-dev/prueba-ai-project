"""TMDB API service for fetching media metadata."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

import requests


logger = logging.getLogger(__name__)


@dataclass
class TMDBSearchResult:
    """Represents a search result from TMDB."""

    tmdb_id: int
    title: str
    original_title: str
    year: int
    media_type: str  # "movie" or "tv"
    poster_path: Optional[str] = None
    overview: str = ""


class TMDBService:
    """Service for interacting with The Movie Database API."""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: str, language: str = "es-ES", log_dir: Optional[str] = None):
        """Initialize TMDB service.

        Args:
            api_key: TMDB API key
            language: Language code for results (default: es-ES)
            log_dir: Directory to store API logs (default: ~/.mediaorganizer/logs)
        """
        self.api_key = api_key
        self.language = language
        self._session = requests.Session()
        self._session.params = {"api_key": api_key, "language": language}
        
        # Setup logging
        if log_dir is None:
            log_dir = str(Path.home() / ".mediaorganizer" / "logs")
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "tmdb_api.log"
        
        # Initialize log file with header
        if not self.log_file.exists():
            self._write_log_header()

    def _write_log_header(self) -> None:
        """Write header to log file."""
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write("# TMDB API Logs - MediaOrganizer\n")
            f.write(f"# Started: {datetime.now().isoformat()}\n")
            f.write("# Format: [TIMESTAMP] METHOD URL | STATUS | QUERY_PARAMS\n")
            f.write("# " + "=" * 80 + "\n\n")

    def _log_request(self, method: str, url: str, params: dict, status_code: int, response_data: Optional[dict] = None) -> None:
        """Log API request and response.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            params: Query parameters
            status_code: HTTP status code
            response_data: Response data (truncated if too large)
        """
        timestamp = datetime.now().isoformat()
        
        # Truncate params for logging (remove api_key for security)
        safe_params = {k: v for k, v in params.items() if k != "api_key"}
        
        # Log request line
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {method} {url}\n")
            f.write(f"  Params: {json.dumps(safe_params, ensure_ascii=False)}\n")
            f.write(f"  Status: {status_code}\n")
            
            # Log response if available (truncated to 500 chars)
            if response_data:
                response_str = json.dumps(response_data, ensure_ascii=False, default=str)
                if len(response_str) > 500:
                    response_str = response_str[:500] + f"... (truncated, total {len(response_str)} chars)"
                f.write(f"  Response: {response_str}\n")
            
            f.write("\n" + "-" * 80 + "\n\n")
        
        logger.debug(f"TMDB API: {method} {url} -> {status_code}")

    def search(self, query: str, year: Optional[int] = None) -> list[TMDBSearchResult]:
        """Search for movies and TV shows.

        Args:
            query: Search query
            year: Optional year filter

        Returns:
            List of TMDBSearchResult objects
        """
        results = []
        params = {"query": query, "include_adult": "false"}
        if year:
            params["year"] = str(year)
        
        url = f"{self.BASE_URL}/search/multi"
        
        # Search multi (movies and TV)
        response = self._session.get(url, params=params)
        
        # Log the request/response
        response_data = None
        if response.status_code == 200:
            response_data = response.json()
        
        self._log_request("GET", url, params, response.status_code, response_data)
        
        if response.status_code == 200 and response_data:
            for item in response_data.get("results", []):
                if item.get("media_type") not in ["movie", "tv"]:
                    continue

                title = item.get("title") or item.get("name", "")
                release_date = item.get("release_date") or item.get("first_air_date", "")
                year_result = int(release_date[:4]) if release_date and len(release_date) >= 4 else None

                # Filter by year if specified
                if year and year_result and year_result != year:
                    continue

                results.append(
                    TMDBSearchResult(
                        tmdb_id=item["id"],
                        title=title,
                        original_title=item.get("original_title") or item.get("original_name", ""),
                        year=year_result or 0,
                        media_type=item["media_type"],
                        poster_path=item.get("poster_path"),
                        overview=item.get("overview", ""),
                    )
                )

        return results

    def get_movie_details(self, tmdb_id: int) -> dict:
        """Get detailed information for a movie.

        Args:
            tmdb_id: TMDB movie ID

        Returns:
            Dictionary with movie details
        """
        url = f"{self.BASE_URL}/movie/{tmdb_id}"
        response = self._session.get(url)
        
        response_data = response.json() if response.status_code == 200 else None
        self._log_request("GET", url, {}, response.status_code, response_data)
        
        if response.status_code == 200:
            return response_data
        return {}

    def get_tv_details(self, tmdb_id: int) -> dict:
        """Get detailed information for a TV show.

        Args:
            tmdb_id: TMDB TV show ID

        Returns:
            Dictionary with TV show details
        """
        url = f"{self.BASE_URL}/tv/{tmdb_id}"
        response = self._session.get(url)
        
        response_data = response.json() if response.status_code == 200 else None
        self._log_request("GET", url, {}, response.status_code, response_data)
        
        if response.status_code == 200:
            return response_data
        return {}

    def get_episode_details(
        self, tv_id: int, season: int, episode: int
    ) -> dict:
        """Get details for a specific episode.

        Args:
            tv_id: TMDB TV show ID
            season: Season number
            episode: Episode number

        Returns:
            Dictionary with episode details
        """
        url = f"{self.BASE_URL}/tv/{tv_id}/season/{season}/episode/{episode}"
        response = self._session.get(url)
        
        response_data = response.json() if response.status_code == 200 else None
        self._log_request("GET", url, {}, response.status_code, response_data)
        
        if response.status_code == 200:
            return response_data
        return {}
