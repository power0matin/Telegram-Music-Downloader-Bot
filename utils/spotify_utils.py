"""
Spotify URL validation and metadata extraction utilities.

This module provides utilities for validating Spotify URLs and extracting metadata.
"""
import re
import requests
import json
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, Any, Tuple
from enum import Enum

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
    
    # Comprehensive Spotify URL patterns
    SPOTIFY_PATTERNS = {
        SpotifyType.TRACK: [
            r'https?://open\.spotify\.com/track/([a-zA-Z0-9]{22})',
            r'https?://spotify\.com/track/([a-zA-Z0-9]{22})',
            r'https?://open\.spotify\.com/(?:[a-z]{2}/)?track/([a-zA-Z0-9]{22})',
            r'spotify:track:([a-zA-Z0-9]{22})',
        ],
        SpotifyType.ALBUM: [
            r'https?://open\.spotify\.com/album/([a-zA-Z0-9]{22})',
            r'https?://spotify\.com/album/([a-zA-Z0-9]{22})',
            r'https?://open\.spotify\.com/(?:[a-z]{2}/)?album/([a-zA-Z0-9]{22})',
            r'spotify:album:([a-zA-Z0-9]{22})',
        ],
        SpotifyType.PLAYLIST: [
            r'https?://open\.spotify\.com/playlist/([a-zA-Z0-9]{22})',
            r'https?://spotify\.com/playlist/([a-zA-Z0-9]{22})',
            r'https?://open\.spotify\.com/(?:[a-z]{2}/)?playlist/([a-zA-Z0-9]{22})',
            r'spotify:playlist:([a-zA-Z0-9]{22})',
        ],
        SpotifyType.ARTIST: [
            r'https?://open\.spotify\.com/artist/([a-zA-Z0-9]{22})',
            r'https?://spotify\.com/artist/([a-zA-Z0-9]{22})',
            r'https?://open\.spotify\.com/(?:[a-z]{2}/)?artist/([a-zA-Z0-9]{22})',
            r'spotify:artist:([a-zA-Z0-9]{22})',
        ]
    }
    
    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """
        Sanitize and normalize a Spotify URL.
        
        Args:
            url: Raw URL string
            
        Returns:
            Sanitized URL string
        """
        if not url:
            return ""
        
        # Remove common junk from URLs
        url = url.strip()
        
        # Remove query parameters and fragments that might cause issues
        parsed = urlparse(url)
        
        # Reconstruct clean URL
        if parsed.netloc and parsed.path:
            # Extract just the core URL without tracking parameters
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            # Handle special cases for sharing URLs
            if "?si=" in url:
                # Remove Spotify sharing tracking
                clean_url = url.split("?si=")[0]
            
            return clean_url
        
        return url
    
    @classmethod
    def validate_and_parse(cls, url: str) -> Tuple[bool, SpotifyType, Optional[str]]:
        """
        Validate Spotify URL and extract information.
        
        Args:
            url: Spotify URL to validate
            
        Returns:
            Tuple of (is_valid, content_type, spotify_id)
        """
        if not url:
            return False, SpotifyType.UNKNOWN, None
        
        # Sanitize the URL first
        clean_url = cls.sanitize_url(url)
        
        # Try to match against all patterns
        for content_type, patterns in cls.SPOTIFY_PATTERNS.items():
            for pattern in patterns:
                match = re.match(pattern, clean_url)
                if match:
                    spotify_id = match.group(1)
                    logger.debug(f"Matched {content_type.value} with ID: {spotify_id}")
                    return True, content_type, spotify_id
        
        # Check for malformed but potentially valid URLs
        if "spotify" in clean_url.lower():
            logger.warning(f"Potentially malformed Spotify URL: {clean_url}")
        
        return False, SpotifyType.UNKNOWN, None
    
    @classmethod
    def is_valid_spotify_url(cls, url: str) -> bool:
        """
        Quick check if URL is a valid Spotify URL.
        
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
        Get canonical Spotify URL from any valid Spotify URL.
        
        Args:
            url: Spotify URL
            
        Returns:
            Canonical open.spotify.com URL or None if invalid
        """
        is_valid, content_type, spotify_id = cls.validate_and_parse(url)
        
        if not is_valid or content_type == SpotifyType.UNKNOWN:
            return None
        
        return f"https://open.spotify.com/{content_type.value}/{spotify_id}"


class SpotifyMetadataExtractor:
    """
    Extract metadata from Spotify URLs using public APIs.
    
    Note: This is a basic implementation. For production use with high volume,
    you should use the official Spotify Web API with proper authentication.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_metadata(self, url: str) -> Dict[str, Any]:
        """
        Extract basic metadata from Spotify URL.
        
        Args:
            url: Spotify URL
            
        Returns:
            Dictionary with extracted metadata
        """
        is_valid, content_type, spotify_id = SpotifyURLValidator.validate_and_parse(url)
        
        if not is_valid:
            return {
                'valid': False,
                'error': 'Invalid Spotify URL'
            }
        
        metadata = {
            'valid': True,
            'type': content_type.value,
            'id': spotify_id,
            'url': SpotifyURLValidator.get_canonical_url(url),
            'title': None,
            'artist': None,
            'album': None,
            'duration_ms': None,
            'image_url': None,
            'external_urls': {},
        }
        
        try:
            # Try to get metadata from Spotify's embed API
            embed_url = f"https://open.spotify.com/embed/{content_type.value}/{spotify_id}"
            
            response = self.session.get(embed_url, timeout=10)
            if response.status_code == 200:
                # Parse basic info from embed page
                html_content = response.text
                
                # Extract title from meta tags
                title_match = re.search(r'<meta property="og:title" content="([^"]*)"', html_content)
                if title_match:
                    metadata['title'] = title_match.group(1)
                
                # Extract description (often contains artist info)
                desc_match = re.search(r'<meta property="og:description" content="([^"]*)"', html_content)
                if desc_match:
                    description = desc_match.group(1)
                    if content_type == SpotifyType.TRACK and "·" in description:
                        # For tracks, description is usually "Artist · Album"
                        parts = description.split("·")
                        if len(parts) >= 1:
                            metadata['artist'] = parts[0].strip()
                        if len(parts) >= 2:
                            metadata['album'] = parts[1].strip()
                
                # Extract image URL
                image_match = re.search(r'<meta property="og:image" content="([^"]*)"', html_content)
                if image_match:
                    metadata['image_url'] = image_match.group(1)
                
                logger.debug(f"Extracted metadata for {content_type.value}: {metadata['title']}")
        
        except Exception as e:
            logger.warning(f"Failed to extract metadata for {url}: {e}")
            metadata['error'] = f"Failed to extract metadata: {str(e)}"
        
        return metadata
    
    def get_track_info(self, url: str) -> Dict[str, Any]:
        """
        Get detailed track information.
        
        Args:
            url: Spotify track URL
            
        Returns:
            Dictionary with track information
        """
        metadata = self.extract_metadata(url)
        
        if not metadata['valid'] or metadata['type'] != 'track':
            return metadata
        
        # Add track-specific processing here if needed
        return metadata


# Global instances
url_validator = SpotifyURLValidator()
metadata_extractor = SpotifyMetadataExtractor()


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
    return metadata_extractor.extract_metadata(url)


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
        url: Spotify URL
        
    Returns:
        Canonical URL or None if invalid
    """
    return url_validator.get_canonical_url(url)