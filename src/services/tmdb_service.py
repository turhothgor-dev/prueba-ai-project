"""TMDB API service for fetching media metadata."""

import requests
from typing import Optional
from dataclasses import dataclass


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

    def search(self, query: str, year: Optional[int] = None) -> list[TMDBSearchResult]:
        """Search for movies and TV shows.

        Args:
            query: Search query
            year: Optional year filter

        Returns:
            List of TMDBSearchResult objects
        """
        results = []

        # Search multi (movies and TV)
        response = self._session.get(
            f"{self.BASE_URL}/search/multi",
            params={"query": query, "include_adult": "false"},
        )

        if response.status_code == 200:
            data = response.json()
            for item in data.get("results", []):
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
        response = self._session.get(f"{self.BASE_URL}/movie/{tmdb_id}")
        if response.status_code == 200:
            return response.json()
        return {}

    def get_tv_details(self, tmdb_id: int) -> dict:
        """Get detailed information for a TV show.

        Args:
            tmdb_id: TMDB TV show ID

        Returns:
            Dictionary with TV show details
        """
        response = self._session.get(f"{self.BASE_URL}/tv/{tmdb_id}")
        if response.status_code == 200:
            return response.json()
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
        response = self._session.get(
            f"{self.BASE_URL}/tv/{tv_id}/season/{season}/episode/{episode}"
        )
        if response.status_code == 200:
            return response.json()
        return {}
