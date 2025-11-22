#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spotify API Connectivity & Auth Test
------------------------------------

Designed by power0matin
GitHub: https://github.com/power0matin/Spotify-API-Test

This script:
- Checks Spotify Client Credentials authentication.
- Prints a nice, colored TUI (terminal UI) using `rich`.
- Writes detailed logs to a file in the `Log` directory.
"""

from __future__ import annotations

import os
import time
import datetime
from typing import Optional, Tuple

import requests
from requests import Session, Response

# Try to load rich; if not available, we fall back to plain prints.
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None  # type: ignore


# -----------------------------
#   Config
# -----------------------------

LOG_DIR = "Log"
GITHUB_LINK = "https://github.com/power0matin/Spotify-API-Test"

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
DEFAULT_TIMEOUT = 10.0  # seconds
CLOCK_SKEW_MARGIN = 30  # seconds


# -----------------------------
#   Logging helpers
# -----------------------------


def ensure_log_dir() -> None:
    """Ensure the log directory exists."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def get_log_file_path() -> str:
    """Generate a timestamped log file path."""
    now = datetime.datetime.now()
    filename = now.strftime("spotify_api_test_%Y-%m-%d_%H-%M-%S.log")
    return os.path.join(LOG_DIR, filename)


def log(message: str, log_file) -> None:
    """Write message to log file with timestamp and print it (plain)."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    log_file.write(full_message + "\n")
    log_file.flush()


# -----------------------------
#   Spotify auth client
# -----------------------------


class SpotifyAuthError(Exception):
    """Base exception for Spotify auth related errors."""


class SpotifyConfigError(SpotifyAuthError):
    """Raised when client_id/client_secret are missing or invalid."""


class SpotifyHTTPError(SpotifyAuthError):
    """Raised when Spotify token endpoint returns a non-200 HTTP status."""

    def __init__(self, status_code: int, body: str):
        super().__init__(
            f"Spotify token request failed with {status_code}: {body[:200]}..."
        )
        self.status_code = status_code
        self.body = body


class SpotifyTokenClient:
    """
    Client for Spotify Client Credentials auth.

    - Reads client_id/client_secret from env if not provided.
    - Caches access token in memory.
    - Refreshes token when expired or when force_refresh=True.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[Session] = None,
        token_url: str = SPOTIFY_TOKEN_URL,
        clock_skew_margin: int = CLOCK_SKEW_MARGIN,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._timeout = float(timeout)
        self._token_url = token_url
        self._clock_skew_margin = int(clock_skew_margin)

        self._session: Session = session or requests.Session()

        # token cache
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0  # unix timestamp

    # Internal helpers
    def _load_credentials(self) -> Tuple[str, str]:
        client_id = self._client_id or os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = self._client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise SpotifyConfigError(
                "SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET is not configured. "
                "Set them as environment variables or pass them to SpotifyTokenClient."
            )

        self._client_id = client_id
        self._client_secret = client_secret
        return client_id, client_secret

    def _request_token_from_spotify(self) -> float:
        """
        Call Spotify token endpoint and update the cached token + expiry.
        Returns the request duration in seconds.
        """
        client_id, client_secret = self._load_credentials()

        data = {
            "grant_type": "client_credentials",
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        start = time.time()
        try:
            resp: Response = self._session.post(
                self._token_url,
                data=data,
                headers=headers,
                auth=(client_id, client_secret),
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise SpotifyAuthError(
                f"Error while calling Spotify token endpoint: {exc}"
            ) from exc
        duration = time.time() - start

        if resp.status_code != 200:
            body_text = resp.text
            raise SpotifyHTTPError(resp.status_code, body_text)

        try:
            payload = resp.json()
        except ValueError as exc:
            raise SpotifyAuthError(
                "Failed to parse JSON from Spotify token endpoint."
            ) from exc

        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in", 3600)

        if not access_token:
            raise SpotifyAuthError("Spotify response did not contain 'access_token'.")

        now = time.time()
        expires_at = now + float(expires_in) - self._clock_skew_margin

        self._access_token = access_token
        self._expires_at = expires_at

        return duration

    def _is_token_valid(self) -> bool:
        if not self._access_token:
            return False
        return time.time() < self._expires_at

    def get_access_token(self, *, force_refresh: bool = False) -> Tuple[str, float]:
        """
        Return a valid access token and last request duration (seconds).

        - If token cache is valid and force_refresh=False, duration will be 0.0.
        - Otherwise a network call happens and duration is >0.
        """
        if force_refresh or not self._is_token_valid():
            duration = self._request_token_from_spotify()
        else:
            duration = 0.0

        assert self._access_token is not None
        return self._access_token, duration

    def seconds_until_expiry(self) -> int:
        if not self._access_token:
            return 0
        return max(0, int(self._expires_at - time.time()))

    def close(self) -> None:
        self._session.close()


# -----------------------------
#   Rich-based UI
# -----------------------------


def render_ui_success(
    token_preview: str,
    expires_in: int,
    duration: float,
    log_path: str,
) -> None:
    """
    Render a nice terminal UI for the success case.
    """
    if not RICH_AVAILABLE:
        # Fallback simple output
        print("Spotify token fetched successfully.")
        print(f"Token (preview): {token_preview}")
        print(f"Approx. seconds until expiry: {expires_in}")
        print(f"Log file: {log_path}")
        return

    console = Console()

    title_text = Text("Spotify API Connectivity Test", style="bold green")
    subtitle_text = Text(
        f"Designed by power0matin | GitHub: {GITHUB_LINK}", style="italic cyan"
    )

    table = Table(
        title="Token & Request Details",
        box=box.ROUNDED,
        expand=False,
        show_edge=True,
        show_header=False,
    )
    table.add_column("Field", style="bold magenta")
    table.add_column("Value", style="white")

    table.add_row("Status", "[bold green]✅ Success[/bold green]")
    table.add_row("Token preview", f"[yellow]{token_preview}[/yellow]")
    table.add_row("Expires in", f"{expires_in} seconds")
    table.add_row("Request time", f"{duration:.3f} seconds")
    table.add_row("Log file", f"[cyan]{log_path}[/cyan]")

    header_panel = Panel.fit(
        Text.assemble(title_text, "\n", subtitle_text),
        border_style="green",
        padding=(1, 2),
    )

    console.print()
    console.print(header_panel)
    console.print()
    console.print(table)
    console.print()


def render_ui_error(error: Exception, log_path: str) -> None:
    """
    Render a nice terminal UI for the error case.
    """
    if not RICH_AVAILABLE:
        print("Spotify token test failed.")
        print(f"Error: {error}")
        print(f"Log file: {log_path}")
        return

    console = Console()

    title_text = Text("Spotify API Connectivity Test", style="bold red")
    subtitle_text = Text(
        f"Designed by power0matin | GitHub: {GITHUB_LINK}", style="italic cyan"
    )

    error_panel = Panel.fit(
        Text(str(error), style="bold red"),
        title="Error",
        border_style="red",
        padding=(1, 2),
    )

    info_table = Table(
        title="Details",
        box=box.ROUNDED,
        expand=False,
        show_edge=True,
        show_header=False,
    )
    info_table.add_column("Field", style="bold magenta")
    info_table.add_column("Value", style="white")

    info_table.add_row("Status", "[bold red]❌ Failed[/bold red]")
    info_table.add_row("Log file", f"[cyan]{log_path}[/cyan]")

    header_panel = Panel.fit(
        Text.assemble(title_text, "\n", subtitle_text),
        border_style="red",
        padding=(1, 2),
    )

    console.print()
    console.print(header_panel)
    console.print()
    console.print(error_panel)
    console.print(info_table)
    console.print()


# -----------------------------
#   Test runner
# -----------------------------


def run_spotify_token_test() -> None:
    """
    Main test:
    - Get a Spotify token using Client Credentials flow.
    - Log details to file.
    - Render pretty terminal UI.
    """
    ensure_log_dir()
    log_path = get_log_file_path()

    client = SpotifyTokenClient()

    with open(log_path, "a", encoding="utf-8") as log_file:
        log("=" * 40, log_file)
        log(f"Designed by power0matin | GitHub: {GITHUB_LINK}", log_file)

        try:
            log("Requesting Spotify access token...", log_file)
            token, duration = client.get_access_token(force_refresh=True)
            expires_in = client.seconds_until_expiry()

            token_preview = token[:12] + "..." if token else "(none)"

            log("✅ Success: Spotify API token endpoint is accessible!", log_file)
            log(f"Token (preview): {token_preview}", log_file)
            log(f"Approx. seconds until expiry: {expires_in}", log_file)
            log(f"Last request time: {duration:.3f} seconds", log_file)

            render_ui_success(
                token_preview=token_preview,
                expires_in=expires_in,
                duration=duration,
                log_path=log_path,
            )

        except Exception as exc:
            # Log full error
            log("❌ Failed to obtain Spotify token.", log_file)
            log(f"Error: {exc}", log_file)
            render_ui_error(exc, log_path)


if __name__ == "__main__":
    run_spotify_token_test()
