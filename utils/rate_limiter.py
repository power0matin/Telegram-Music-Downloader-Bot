"""
Rate limiting system for Spotify Bot.

This module implements rate limiting to prevent spam and abuse.
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass
from threading import Lock

from config import config


@dataclass
class UserRateLimit:
    """Rate limit data for a user."""

    request_count: int = 0
    window_start: float = 0.0
    last_request: float = 0.0


class RateLimiter:
    """
    Rate limiter implementation using sliding window.

    This class manages rate limiting per user to prevent spam and abuse.
    """

    def __init__(self, max_requests: int = None, window_seconds: int = None):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window (uses config default if None)
            window_seconds: Time window in seconds (uses config default if None)
        """
        self.max_requests = max_requests or config.rate_limit_requests
        self.window_seconds = window_seconds or config.rate_limit_window_seconds
        self.user_limits: Dict[int, UserRateLimit] = {}
        self.lock = Lock()

    def is_allowed(self, user_id: int) -> tuple[bool, Optional[float]]:
        """
        Check if a request is allowed for the user.

        Args:
            user_id: Telegram user ID

        Returns:
            Tuple of (is_allowed, time_until_allowed)
            - is_allowed: True if request is allowed
            - time_until_allowed: Seconds until next request is allowed (None if allowed)
        """
        with self.lock:
            current_time = time.time()

            # Get or create user rate limit data
            if user_id not in self.user_limits:
                self.user_limits[user_id] = UserRateLimit()

            user_limit = self.user_limits[user_id]

            # Check if we need to reset the window
            if current_time - user_limit.window_start >= self.window_seconds:
                user_limit.request_count = 0
                user_limit.window_start = current_time

            # Check if user has exceeded the limit
            if user_limit.request_count >= self.max_requests:
                time_until_reset = self.window_seconds - (
                    current_time - user_limit.window_start
                )
                return False, max(0, time_until_reset)

            # Request is allowed
            user_limit.request_count += 1
            user_limit.last_request = current_time

            return True, None

    def get_user_stats(self, user_id: int) -> Dict[str, any]:
        """
        Get rate limit statistics for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            Dictionary with user's rate limit statistics
        """
        with self.lock:
            if user_id not in self.user_limits:
                return {
                    "requests_made": 0,
                    "requests_remaining": self.max_requests,
                    "window_start": 0,
                    "window_end": 0,
                    "last_request": 0,
                }

            user_limit = self.user_limits[user_id]
            current_time = time.time()

            # Check if window has expired
            if current_time - user_limit.window_start >= self.window_seconds:
                requests_made = 0
            else:
                requests_made = user_limit.request_count

            return {
                "requests_made": requests_made,
                "requests_remaining": max(0, self.max_requests - requests_made),
                "window_start": user_limit.window_start,
                "window_end": user_limit.window_start + self.window_seconds,
                "last_request": user_limit.last_request,
            }

    def reset_user(self, user_id: int):
        """
        Reset rate limit for a specific user.

        Args:
            user_id: Telegram user ID
        """
        with self.lock:
            if user_id in self.user_limits:
                del self.user_limits[user_id]

    def cleanup_expired(self):
        """
        Clean up expired rate limit entries to prevent memory leaks.

        This should be called periodically to remove old entries.
        """
        with self.lock:
            current_time = time.time()
            expired_users = []

            for user_id, user_limit in self.user_limits.items():
                # Remove entries that are older than window + some buffer time
                if current_time - user_limit.last_request > self.window_seconds * 2:
                    expired_users.append(user_id)

            for user_id in expired_users:
                del self.user_limits[user_id]


# Global rate limiter instance
rate_limiter = RateLimiter()


def check_rate_limit(user_id: int) -> tuple[bool, Optional[float]]:
    """
    Convenience function to check rate limit for a user.

    Args:
        user_id: Telegram user ID

    Returns:
        Tuple of (is_allowed, time_until_allowed)
    """
    return rate_limiter.is_allowed(user_id)


def get_rate_limit_stats(user_id: int) -> Dict[str, any]:
    """
    Convenience function to get rate limit stats for a user.

    Args:
        user_id: Telegram user ID

    Returns:
        Dictionary with user's rate limit statistics
    """
    return rate_limiter.get_user_stats(user_id)


def reset_user_rate_limit(user_id: int):
    """
    Convenience function to reset rate limit for a user.

    Args:
        user_id: Telegram user ID
    """
    rate_limiter.reset_user(user_id)


def cleanup_expired_rate_limits():
    """
    Convenience function to clean up expired rate limit entries.
    """
    rate_limiter.cleanup_expired()
