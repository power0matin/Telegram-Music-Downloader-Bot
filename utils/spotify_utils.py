"""
Spotify URL validation and metadata extraction utilities.

This module provides utilities for validating Spotify URLs and extracting metadata.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse

import requests

from utils.logging_config import setup_logging

logger = setup_logging(__name__)


class SpotifyType(Enum):
    """Enum for Spotify content types."""

    TRACK = "track"
    ALBUM = "album"
    PLAYLIST = "playlist"
    ARTIST = "artist"
    UNKNOWN = "unknown"


class SpotifyURLValidator:
    """
    Spotify URL validator and parser.

    This class handles validation, sanitization, and parsing of Spotify URLs.
    """

    # Base62 ID used by Spotify: 22 characters [A-Za-z0-9]
    _ID_PATTERN = r"([A-Za-z0-9]{22})"

    # Comprehensive Spotify URL patterns (compatible with intl-* URLs and URIs)
    _PATTERN_STRINGS = {
        SpotifyType.TRACK: [
            rf"https?://open\.spotify\.com/track/{_ID_PATTERN}",
            rf"https?://spotify\.com/track/{_ID_PATTERN}",
            rf"https?://open\.spotify\.com/(?:[A-Za-z-]+/)?track/{_ID_PATTERN}",
            rf"spotify:track:{_ID_PATTERN}",
        ],
        SpotifyType.ALBUM: [
            rf"https?://open\.spotify\.com/album/{_ID_PATTERN}",
            rf"https?://spotify\.com/album/{_ID_PATTERN}",
            rf"https?://open\.spotify\.com/(?:[A-Za-z-]+/)?album/{_ID_PATTERN}",
            rf"spotify:album:{_ID_PATTERN}",
        ],
        SpotifyType.PLAYLIST: [
            rf"https?://open\.spotify\.com/playlist/{_ID_PATTERN}",
            rf"https?://spotify\.com/playlist/{_ID_PATTERN}",
            rf"https?://open\.spotify\.com/(?:[A-Za-z-]+/)?playlist/{_ID_PATTERN}",
            rf"spotify:playlist:{_ID_PATTERN}",
        ],
        SpotifyType.ARTIST: [
            rf"https?://open\.spotify\.com/artist/{_ID_PATTERN}",
            rf"https?://spotify\.com/artist/{_ID_PATTERN}",
            rf"https?://open\.spotify\.com/(?:[A-Za-z-]+/)?artist/{_ID_PATTERN}",
            rf"spotify:artist:{_ID_PATTERN}",
        ],
    }

    # Compile regex patterns once at import time for better performance
    SPOTIFY_PATTERNS = {
        content_type: [re.compile(pattern) for pattern in patterns]
        for content_type, patterns in _PATTERN_STRINGS.items()
    }

    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """
        Sanitize and normalize a Spotify URL/URI.

        - Strips whitespace
        - Removes query parameters and fragments for http(s) URLs
        - Leaves spotify: URIs as-is

        Args:
            url: Raw URL string

        Returns:
            Sanitized URL string (may still be invalid as a Spotify URL)
        """
        if not url:
            return ""

        url = url.strip()

        # spotify:track:... یا spotify:album:...
        if url.lower().startswith("spotify:"):
            return url

        parsed = urlparse(url)

        if parsed.scheme and parsed.netloc and parsed.path:
            # Reconstruct without query/fragment
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            return clean_url

        return url

    @classmethod
    def validate_and_parse(cls, url: str) -> Tuple[bool, SpotifyType, Optional[str]]:
        """
        Validate Spotify URL and extract information.

        Args:
            url: Spotify URL/URI to validate

        Returns:
            Tuple of (is_valid, content_type, spotify_id)
        """
        if not url:
            return False, SpotifyType.UNKNOWN, None

        clean_url = cls.sanitize_url(url)

        for content_type, patterns in cls.SPOTIFY_PATTERNS.items():
            for pattern in patterns:
                match = pattern.fullmatch(clean_url)
                if match:
                    spotify_id = match.group(1)
                    logger.debug(
                        "Matched %s with ID: %s",
                        content_type.value,
                        spotify_id,
                    )
                    return True, content_type, spotify_id

        if "spotify" in clean_url.lower():
            logger.warning("Potentially malformed Spotify URL: %s", clean_url)

        return False, SpotifyType.UNKNOWN, None

    @classmethod
    def is_valid_spotify_url(cls, url: str) -> bool:
        """
        Quick check if URL is a valid Spotify URL of a known type.

        Args:
            url: URL to check

        Returns:
            True if valid Spotify URL
        """
        is_valid, _, _ = cls.validate_and_parse(url)
        return is_valid

    @classmethod
    def get_canonical_url(cls, url: str) -> Optional[str]:
        """
        Get canonical Spotify URL from any valid Spotify URL/URI.

        Canonical form:
            https://open.spotify.com/<type>/<id>

        Args:
            url: Spotify URL/URI

        Returns:
            Canonical open.spotify.com URL or None if invalid
        """
        is_valid, content_type, spotify_id = cls.validate_and_parse(url)

        if not is_valid or content_type == SpotifyType.UNKNOWN or not spotify_id:
            return None

        return f"https://open.spotify.com/{content_type.value}/{spotify_id}"


class SpotifyMetadataExtractor:
    """
    Extract metadata from Spotify URLs using public endpoints.

    For reliability, this uses the official oEmbed endpoint where possible,
    with a lightweight HTML fallback if required.
    """

    OEMBED_URL = "https://open.spotify.com/oembed"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                )
            }
        )

    def close(self) -> None:
        """Close the underlying requests session to release resources."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def extract_metadata(self, url: str) -> Dict[str, Any]:
        """
        Extract basic metadata from Spotify URL.

        Args:
            url: Spotify URL/URI

        Returns:
            Dictionary with extracted metadata
        """
        is_valid, content_type, spotify_id = SpotifyURLValidator.validate_and_parse(url)

        if not is_valid or not spotify_id:
            return {"valid": False, "error": "Invalid Spotify URL"}

        canonical_url = SpotifyURLValidator.get_canonical_url(url)

        metadata: Dict[str, Any] = {
            "valid": True,
            "type": content_type.value,
            "id": spotify_id,
            "url": canonical_url,
            "title": None,
            "artist": None,
            "album": None,
            "duration_ms": None,
            "image_url": None,
            "external_urls": {},
        }

        # 1) Try oEmbed endpoint (JSON, stable)
        try:
            resp = self.session.get(
                self.OEMBED_URL,
                params={"url": canonical_url},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()

                # Example oEmbed fields: title, author_name, thumbnail_url, provider_url, etc.
                metadata["title"] = data.get("title")
                metadata["image_url"] = data.get("thumbnail_url")
                metadata["external_urls"]["spotify"] = canonical_url

                author_name = data.get("author_name")
                if content_type == SpotifyType.TRACK and author_name:
                    # Often "Artist" or "Artist, Other Artist"
                    metadata["artist"] = author_name

                logger.debug(
                    "Extracted metadata via oEmbed for %s: %s",
                    content_type.value,
                    metadata["title"],
                )
                return metadata
            else:
                logger.warning(
                    "oEmbed request failed for %s (status %s)",
                    canonical_url,
                    resp.status_code,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("oEmbed metadata fetch failed for %s: %s", url, exc)

        # 2) Fallback: embed page HTML scraping for minimal info
        try:
            embed_url = (
                f"https://open.spotify.com/embed/{content_type.value}/{spotify_id}"
            )
            response = self.session.get(embed_url, timeout=10)

            if response.status_code == 200:
                html_content = response.text

                # Title from og:title
                title_match = re.search(
                    r'<meta property="og:title" content="([^"]*)"', html_content
                )
                if title_match:
                    metadata["title"] = title_match.group(1)

                # Description often contains artist/album
                desc_match = re.search(
                    r'<meta property="og:description" content="([^"]*)"',
                    html_content,
                )
                if desc_match:
                    description = desc_match.group(1)
                    if content_type == SpotifyType.TRACK and "·" in description:
                        parts = [p.strip() for p in description.split("·")]
                        if len(parts) >= 1:
                            metadata["artist"] = parts[0] or None
                        if len(parts) >= 2:
                            metadata["album"] = parts[1] or None

                # Image
                image_match = re.search(
                    r'<meta property="og:image" content="([^"]*)"', html_content
                )
                if image_match:
                    metadata["image_url"] = image_match.group(1)

                logger.debug(
                    "Extracted metadata via HTML for %s: %s",
                    content_type.value,
                    metadata["title"],
                )

        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to extract metadata for %s: %s", url, exc)
            metadata["error"] = f"Failed to extract metadata: {exc}"

        return metadata

    def get_track_info(self, url: str) -> Dict[str, Any]:
        """
        Get detailed track information (currently thin wrapper over extract_metadata).

        Args:
            url: Spotify track URL

        Returns:
            Dictionary with track information
        """
        metadata = self.extract_metadata(url)

        if not metadata.get("valid") or metadata.get("type") != "track":
            return metadata

        # Future: add track-specific processing here
        return metadata


# Stateless validator can be shared safely across handler threads.
url_validator = SpotifyURLValidator()


def validate_spotify_url(url: str) -> bool:
    """
    Convenience function to validate Spotify URL.

    Args:
        url: URL to validate

    Returns:
        True if valid Spotify URL
    """
    return url_validator.is_valid_spotify_url(url)


def get_spotify_metadata(url: str) -> Dict[str, Any]:
    """
    Convenience function to get Spotify metadata.

    Args:
        url: Spotify URL

    Returns:
        Dictionary with metadata
    """
    # requests.Session is mutable and not guaranteed to be thread-safe. Each
    # Telegram handler gets its own short-lived session instead of sharing one
    # global session across concurrent users.
    with SpotifyMetadataExtractor() as extractor:
        return extractor.extract_metadata(url)


def sanitize_spotify_url(url: str) -> str:
    """
    Convenience function to sanitize Spotify URL.

    Args:
        url: URL to sanitize

    Returns:
        Sanitized URL
    """
    return url_validator.sanitize_url(url)


def get_canonical_spotify_url(url: str) -> Optional[str]:
    """
    Convenience function to get canonical Spotify URL.

    Args:
        url: Spotify URL/URI

    Returns:
        Canonical URL or None if invalid
    """
    return url_validator.get_canonical_url(url)
