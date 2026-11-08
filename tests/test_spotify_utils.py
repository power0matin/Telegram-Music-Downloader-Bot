"""
Tests for Spotify utilities module.

This module contains tests for URL validation, metadata extraction,
and other Spotify-related utilities.
"""

import pytest
from unittest.mock import patch, Mock

from utils.spotify_utils import (
    validate_spotify_url,
    sanitize_spotify_url,
    get_canonical_spotify_url,
    SpotifyURLValidator,
    SpotifyType,
)


class TestSpotifyURLValidator:
    """Test cases for Spotify URL validation."""

    def test_valid_track_urls(self):
        """Test validation of valid track URLs."""
        valid_urls = [
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            "https://spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            "https://open.spotify.com/en/track/4iV5W9uYEdYUVa79Axb7Rh",
            "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
        ]

        for url in valid_urls:
            assert validate_spotify_url(url), f"URL should be valid: {url}"

    def test_valid_album_urls(self):
        """Test validation of valid album URLs."""
        valid_urls = [
            "https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3",
            "https://spotify.com/album/1DFixLWuPkv3KT3TnV35m3",
            "spotify:album:1DFixLWuPkv3KT3TnV35m3",
        ]

        for url in valid_urls:
            assert validate_spotify_url(url), f"URL should be valid: {url}"

    def test_valid_playlist_urls(self):
        """Test validation of valid playlist URLs."""
        valid_urls = [
            "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd",
            "https://spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd",
            "spotify:playlist:37i9dQZF1DX0XUsuxWHRQd",
        ]

        for url in valid_urls:
            assert validate_spotify_url(url), f"URL should be valid: {url}"

    def test_invalid_urls(self):
        """Test validation of invalid URLs."""
        invalid_urls = [
            "https://youtube.com/watch?v=abc123",
            "https://apple.music/album/test",
            "not a url at all",
            "",
            None,
            "https://open.spotify.com/invalid/abc123",
            "spotify:invalid:abc123",
        ]

        for url in invalid_urls:
            assert not validate_spotify_url(url), f"URL should be invalid: {url}"

    def test_url_sanitization(self):
        """Test URL sanitization functionality."""
        test_cases = [
            (
                "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh?si=abc123",
                "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            ),
            (
                "  https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh  ",
                "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            ),
            ("", ""),
        ]

        for input_url, expected_output in test_cases:
            result = sanitize_spotify_url(input_url)
            assert (
                result == expected_output
            ), f"Expected {expected_output}, got {result}"

    def test_canonical_url_generation(self):
        """Test canonical URL generation."""
        test_cases = [
            (
                "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh?si=abc123",
                "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            ),
            (
                "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
                "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            ),
            ("invalid_url", None),
        ]

        for input_url, expected_output in test_cases:
            result = get_canonical_spotify_url(input_url)
            assert (
                result == expected_output
            ), f"Expected {expected_output}, got {result}"

    def test_validate_and_parse(self):
        """Test URL validation and parsing."""
        # Test valid track URL
        is_valid, content_type, spotify_id = SpotifyURLValidator.validate_and_parse(
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        )

        assert is_valid
        assert content_type == SpotifyType.TRACK
        assert spotify_id == "4iV5W9uYEdYUVa79Axb7Rh"

        # Test invalid URL
        is_valid, content_type, spotify_id = SpotifyURLValidator.validate_and_parse(
            "invalid_url"
        )

        assert not is_valid
        assert content_type == SpotifyType.UNKNOWN
        assert spotify_id is None


class TestSpotifyMetadataExtractor:
    """Test cases for Spotify metadata extraction."""

    @patch("utils.spotify_utils.requests.Session.get")
    def test_metadata_extraction_success(self, mock_get):
        """Test successful metadata extraction."""
        # Mock oEmbed JSON response (first call)
        mock_oembed_response = Mock()
        mock_oembed_response.status_code = 200
        mock_oembed_response.json.return_value = {
            "title": "Never Gonna Give You Up",
            "author_name": "Rick Astley",
            "thumbnail_url": "https://example.com/image.jpg",
        }

        mock_get.return_value = mock_oembed_response

        from utils.spotify_utils import SpotifyMetadataExtractor

        extractor = SpotifyMetadataExtractor()

        metadata = extractor.extract_metadata(
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        )

        assert metadata["valid"]
        assert metadata["type"] == "track"
        assert metadata["title"] == "Never Gonna Give You Up"
        assert metadata["artist"] == "Rick Astley"
        assert metadata["external_urls"]["spotify"] == (
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        )
        assert "image_url" not in metadata
        mock_get.assert_called_once_with(
            "https://open.spotify.com/oembed",
            params={
                "url": "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
            },
            timeout=10,
        )

    @patch("utils.spotify_utils.requests.Session.get")
    def test_oembed_failure_does_not_scrape_embed_html(self, mock_get):
        from utils.spotify_utils import SpotifyMetadataExtractor

        response = Mock()
        response.status_code = 403
        mock_get.return_value = response

        with SpotifyMetadataExtractor() as extractor:
            metadata = extractor.extract_metadata(
                "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
            )

        assert metadata["valid"] is True
        assert metadata["title"] is None
        assert metadata["external_urls"]["spotify"] == (
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        )
        assert "image_url" not in metadata
        mock_get.assert_called_once()


    def test_metadata_extraction_invalid_url(self):
        """Test metadata extraction with invalid URL."""
        from utils.spotify_utils import SpotifyMetadataExtractor

        extractor = SpotifyMetadataExtractor()

        metadata = extractor.extract_metadata("invalid_url")

        assert not metadata["valid"]
        assert "error" in metadata


if __name__ == "__main__":
    pytest.main([__file__])
