"""TMDB API service for fetching media metadata."""

import json
import logging
import time
from dataclasses import dataclass

import requests

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TMDBSearchResult:
    """Represents a search result from TMDB."""

    tmdb_id: int
    title: str
    original_title: str
    year: int
    media_type: str  # "movie" or "tv"
    poster_path: str | None = None
    overview: str = ""


class TMDBService:
    """Service for interacting with The Movie Database API."""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: str, language: str = "es-ES"):
        """Initialize TMDB service.

        Args:
            api_key: TMDB API key
            language: Language code for results (default: es-ES)
        """
        self.api_key = api_key
        self.language = language
        self._session = requests.Session()
        self._session.params = {"api_key": api_key, "language": language}

        logger.info("TMDBService initialized (language=%s)", language)

    def _log_request(
        self,
        method: str,
        url: str,
        params: dict,
        status_code: int,
        response_data: dict | None = None,
        elapsed: float = 0.0,
    ) -> None:
        """Log API request and response with appropriate log level.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            params: Query parameters
            status_code: HTTP status code
            response_data: Response data (truncated if too large)
            elapsed: Request duration in seconds
        """
        # Truncate params for logging (remove api_key for security)
        safe_params = {k: v for k, v in params.items() if k != "api_key"}

        # Log at appropriate level based on status code
        if status_code >= 500:
            logger.error(
                "TMDB API ERROR: %s %s | Status: %d | Time: %.2fs | Params: %s",
                method,
                url,
                status_code,
                elapsed,
                json.dumps(safe_params, ensure_ascii=False),
            )
        elif status_code >= 400:
            logger.warning(
                "TMDB API WARNING: %s %s | Status: %d | Time: %.2fs | Params: %s",
                method,
                url,
                status_code,
                elapsed,
                json.dumps(safe_params, ensure_ascii=False),
            )
        else:
            logger.debug(
                "TMDB API: %s %s | Status: %d | Time: %.2fs | Params: %s",
                method,
                url,
                status_code,
                elapsed,
                json.dumps(safe_params, ensure_ascii=False),
            )

        # Log response data for errors or when explicitly provided
        if response_data and (status_code >= 400 or logger.isEnabledFor(logging.DEBUG)):
            response_str = json.dumps(response_data, ensure_ascii=False, default=str)
            # Truncate large responses
            if len(response_str) > 500:
                response_str = (
                    response_str[:500] + f"... (truncated, total {len(response_str)} chars)"
                )
            logger.debug("TMDB Response: %s", response_str)

    def search(self, query: str, year: int | None = None) -> list[TMDBSearchResult]:
        """Search for movies and TV shows.

        Args:
            query: Search query
            year: Optional year filter

        Returns:
            List of TMDBSearchResult objects
        """
        results: list[TMDBSearchResult] = []
        params = {"query": query, "include_adult": "false"}
        if year:
            params["year"] = str(year)

        url = f"{self.BASE_URL}/search/multi"

        # Measure request time
        start_time = time.time()

        try:
            response = self._session.get(url, params=params)
            elapsed = time.time() - start_time

            # Parse response
            response_data = None
            if response.status_code == 200:
                response_data = response.json()

            # Log the request/response
            self._log_request("GET", url, params, response.status_code, response_data, elapsed)

            # Process results
            if response.status_code == 200 and response_data:
                for item in response_data.get("results", []):
                    if item.get("media_type") not in ["movie", "tv"]:
                        continue

                    title = item.get("title") or item.get("name", "")
                    release_date = item.get("release_date") or item.get("first_air_date", "")
                    year_result = (
                        int(release_date[:4]) if release_date and len(release_date) >= 4 else None
                    )

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
                logger.debug("Search '%s': found %d results", query, len(results))
            else:
                logger.warning("Search '%s': no results or API error (status=%d)", query, response.status_code)

        except requests.exceptions.Timeout as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API timeout: %s %s | %.2fs | %s", "GET", url, elapsed, e)
        except requests.exceptions.ConnectionError as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API connection error: %s %s | %.2fs | %s", "GET", url, elapsed, e)
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API request error: %s %s | %.2fs | %s", "GET", url, elapsed, e)

        return results

    def get_movie_details(self, tmdb_id: int) -> dict:
        """Get detailed information for a movie.

        Args:
            tmdb_id: TMDB movie ID

        Returns:
            Dictionary with movie details
        """
        url = f"{self.BASE_URL}/movie/{tmdb_id}"

        start_time = time.time()

        try:
            response = self._session.get(url)
            elapsed = time.time() - start_time

            response_data = response.json() if response.status_code == 200 else None
            self._log_request("GET", url, {}, response.status_code, response_data, elapsed)

            if response.status_code == 200:
                logger.debug("Fetched movie details for ID %d", tmdb_id)
                return response_data
            logger.warning("Failed to fetch movie details for ID %d (status=%d)", tmdb_id, response.status_code)
            return {}

        except requests.exceptions.Timeout as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API timeout fetching movie %d: %.2fs | %s", tmdb_id, elapsed, e)
        except requests.exceptions.ConnectionError as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API connection error fetching movie %d: %.2fs | %s", tmdb_id, elapsed, e)
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API request error fetching movie %d: %.2fs | %s", tmdb_id, elapsed, e)

        return {}

    def get_tv_details(self, tmdb_id: int) -> dict:
        """Get detailed information for a TV show.

        Args:
            tmdb_id: TMDB TV show ID

        Returns:
            Dictionary with TV show details
        """
        url = f"{self.BASE_URL}/tv/{tmdb_id}"

        start_time = time.time()

        try:
            response = self._session.get(url)
            elapsed = time.time() - start_time

            response_data = response.json() if response.status_code == 200 else None
            self._log_request("GET", url, {}, response.status_code, response_data, elapsed)

            if response.status_code == 200:
                logger.debug("Fetched TV details for ID %d", tmdb_id)
                return response_data
            logger.warning("Failed to fetch TV details for ID %d (status=%d)", tmdb_id, response.status_code)
            return {}

        except requests.exceptions.Timeout as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API timeout fetching TV show %d: %.2fs | %s", tmdb_id, elapsed, e)
        except requests.exceptions.ConnectionError as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API connection error fetching TV show %d: %.2fs | %s", tmdb_id, elapsed, e)
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API request error fetching TV show %d: %.2fs | %s", tmdb_id, elapsed, e)

        return {}

    def get_episode_details(self, tv_id: int, season: int, episode: int) -> dict:
        """Get details for a specific episode.

        Args:
            tv_id: TMDB TV show ID
            season: Season number
            episode: Episode number

        Returns:
            Dictionary with episode details
        """
        url = f"{self.BASE_URL}/tv/{tv_id}/season/{season}/episode/{episode}"

        start_time = time.time()

        try:
            response = self._session.get(url)
            elapsed = time.time() - start_time

            response_data = response.json() if response.status_code == 200 else None
            self._log_request("GET", url, {}, response.status_code, response_data, elapsed)

            if response.status_code == 200:
                logger.debug("Fetched episode S%dE%d details for TV show %d", season, episode, tv_id)
                return response_data
            logger.warning("Failed to fetch episode S%dE%d for TV show %d (status=%d)", season, episode, tv_id, response.status_code)
            return {}

        except requests.exceptions.Timeout as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API timeout fetching episode S%dE%d of TV show %d: %.2fs | %s", season, episode, tv_id, elapsed, e)
        except requests.exceptions.ConnectionError as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API connection error fetching episode S%dE%d of TV show %d: %.2fs | %s", season, episode, tv_id, elapsed, e)
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            logger.error("TMDB API request error fetching episode S%dE%d of TV show %d: %.2fs | %s", season, episode, tv_id, elapsed, e)

        return {}
