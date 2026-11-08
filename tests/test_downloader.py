import shutil
import subprocess
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import utils.downloader as downloader_module
from utils.downloader import DownloadError, DownloadResult, SpotifyDownloader


SPOTIFY_URL = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"


def test_spotdl_command_matches_46_cli(tmp_path):
    downloader = SpotifyDownloader(download_dir=str(tmp_path))
    command = downloader._prepare_download_command(
        SPOTIFY_URL, str(tmp_path), quality=320
    )

    assert command[:3] == ["spotdl", "download", SPOTIFY_URL]
    assert "--audio" in command
    assert "--audio-providers" not in command
    audio_index = command.index("--audio")
    assert command[audio_index + 1:audio_index + 4] == [
        "soundcloud",
        "youtube-music",
        "youtube",
    ]
    assert command[command.index("--save-errors") + 1] == str(
        tmp_path / ".spotdl-errors.txt"
    )
    assert command[command.index("--bitrate") + 1] == "320k"
    assert command[command.index("--format") + 1] == "mp3"


def test_installed_spotdl_exposes_expected_cli():
    spotdl = shutil.which("spotdl")
    assert spotdl is not None
    assert version("spotdl") == "4.6.0"

    result = subprocess.run(
        [spotdl, "--help"],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0

    for option in (
        "download",
        "--audio",
        "--bitrate",
        "--format",
        "--output",
        "--overwrite",
        "--max-filename-length",
        "--cookie-file",
        "--proxy",
        "--yt-dlp-args",
        "--save-errors",
    ):
        assert option in output


def test_spotdl_46_dependency_excludes_known_broken_ytmusicapi_releases():
    assert version("ytmusicapi") not in {"1.12.2", "1.12.3"}


def test_spotdl_error_report_ignores_timestamp_and_deduplicates(tmp_path):
    error_file = tmp_path / ".spotdl-errors.txt"
    error_file.write_text(
        "2026-11-08-12-00-00\n"
        "track-a - LookupError: not found\n"
        "track-a - LookupError: not found\n"
        "track-b - AudioProviderError: unavailable\n",
        encoding="utf-8",
    )

    assert downloader_module.SpotifyDownloader._read_spotdl_errors(str(error_file)) == [
        "track-a - LookupError: not found",
        "track-b - AudioProviderError: unavailable",
    ]


def test_download_requests_are_isolated_and_partial_files_are_kept(
    monkeypatch, tmp_path
):
    downloader = SpotifyDownloader(download_dir=str(tmp_path))
    monkeypatch.setattr(
        downloader,
        "check_dependencies",
        lambda: {"spotdl": True, "ffmpeg": True},
    )
    monkeypatch.setattr(
        downloader_module,
        "get_spotify_metadata",
        lambda _url: {"valid": True, "type": "track"},
    )

    created_dirs = []

    def fail_after_creating_one_file(command):
        output_template = command[command.index("--output") + 1]
        request_dir = Path(output_template).parent
        created_dirs.append(request_dir)
        (request_dir / "Artist - Track.mp3").write_bytes(b"audio")
        raise DownloadError("Audio provider error - all configured sources failed")

    monkeypatch.setattr(downloader, "_execute_download", fail_after_creating_one_file)

    first = downloader.download(SPOTIFY_URL, user_id=42, quality=128)
    second = downloader.download(SPOTIFY_URL, user_id=42, quality=128)

    assert first.success and second.success
    assert first.warning and second.warning
    assert first.download_dir != second.download_dir
    assert created_dirs[0] != created_dirs[1]
    assert Path(first.files[0]).parent != Path(second.files[0]).parent

    shutil.rmtree(first.download_dir)
    shutil.rmtree(second.download_dir)


def test_success_exit_with_saved_item_error_is_reported_as_partial(
    monkeypatch, tmp_path
):
    downloader = SpotifyDownloader(download_dir=str(tmp_path))
    monkeypatch.setattr(
        downloader,
        "check_dependencies",
        lambda: {"spotdl": True, "ffmpeg": True},
    )
    monkeypatch.setattr(
        downloader_module,
        "get_spotify_metadata",
        lambda _url: {"valid": True, "type": "playlist"},
    )

    def create_partial_result(command):
        output_template = command[command.index("--output") + 1]
        request_dir = Path(output_template).parent
        error_file = Path(command[command.index("--save-errors") + 1])
        error_file.write_text(
            "2026-11-08-12-00-00\\n"
            "https://open.spotify.com/track/0000000000000000000000 - "
            "LookupError: No results found for song\\n",
            encoding="utf-8",
        )
        (request_dir / "Artist - Available.mp3").write_bytes(b"audio")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(downloader, "_execute_download", create_partial_result)

    result = downloader.download(SPOTIFY_URL, user_id=42, quality=320)

    assert result.success
    assert len(result.files) == 1
    assert result.source_failed_count == 1
    assert result.skipped_file_count == 0
    assert "1 source item(s) failed" in result.warning
    shutil.rmtree(result.download_dir)


def test_mixed_valid_and_oversized_outputs_are_reported_as_partial(
    monkeypatch, tmp_path
):
    downloader = SpotifyDownloader(download_dir=str(tmp_path))
    downloader.max_file_size = 4
    monkeypatch.setattr(
        downloader,
        "check_dependencies",
        lambda: {"spotdl": True, "ffmpeg": True},
    )
    monkeypatch.setattr(
        downloader_module,
        "get_spotify_metadata",
        lambda _url: {"valid": True, "type": "playlist"},
    )

    def create_mixed_outputs(command):
        output_template = command[command.index("--output") + 1]
        request_dir = Path(output_template).parent
        (request_dir / "Artist - Available.mp3").write_bytes(b"ok")
        (request_dir / "Artist - Too Large.mp3").write_bytes(b"oversized")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(downloader, "_execute_download", create_mixed_outputs)

    result = downloader.download(SPOTIFY_URL, user_id=42, quality=320)

    assert result.success
    assert len(result.files) == 1
    assert result.skipped_file_count == 1
    assert result.oversized_file_count == 1
    assert "1 local audio file(s) skipped" in result.warning
    shutil.rmtree(result.download_dir)


def test_partial_source_and_skip_counts_are_reported_to_user(monkeypatch, tmp_path):
    request_dir = tmp_path / "request"
    request_dir.mkdir()
    audio_path = request_dir / "Artist - Track.mp3"
    audio_path.write_bytes(b"audio")
    result = DownloadResult(
        success=True,
        files=[str(audio_path)],
        warning="2 source item(s) failed; 1 local audio file(s) skipped",
        source_failed_count=2,
        skipped_file_count=1,
        download_dir=str(request_dir),
    )

    monkeypatch.setattr(
        SpotifyDownloader,
        "check_dependencies",
        lambda _self: {"spotdl": True, "ffmpeg": True},
    )
    monkeypatch.setattr(
        SpotifyDownloader,
        "download",
        lambda _self, _url, _user_id, _quality: result,
    )

    bot = Mock()
    bot.send_audio.return_value = object()
    message = SimpleNamespace(
        chat=SimpleNamespace(id=-100123456),
        message_thread_id=None,
    )

    downloader_module.download_and_send(
        bot,
        message,
        SPOTIFY_URL,
        quality=320,
        user_id=987654,
    )

    sent_messages = [call.args[1] for call in bot.send_message.call_args_list]
    assert any("2 source item(s) failed" in text for text in sent_messages)
    assert any("1 local audio file(s) skipped" in text for text in sent_messages)
    assert not request_dir.exists()


def test_oversized_audio_returns_delivery_specific_error(monkeypatch, tmp_path):
    downloader = SpotifyDownloader(download_dir=str(tmp_path))
    downloader.max_file_size = 3
    monkeypatch.setattr(
        downloader,
        "check_dependencies",
        lambda: {"spotdl": True, "ffmpeg": True},
    )
    monkeypatch.setattr(
        downloader_module,
        "get_spotify_metadata",
        lambda _url: {"valid": True, "type": "track"},
    )

    def create_oversized_file(command):
        output_template = command[command.index("--output") + 1]
        (Path(output_template).parent / "Artist - Track.mp3").write_bytes(b"audio")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(downloader, "_execute_download", create_oversized_file)

    result = downloader.download(SPOTIFY_URL, user_id=42, quality=320)

    assert not result.success
    assert "size limit" in result.error.lower()
    shutil.rmtree(result.download_dir)


def test_group_download_uploads_to_origin_chat_and_retries_timeout(
    monkeypatch, tmp_path
):
    request_dir = tmp_path / "request"
    request_dir.mkdir()
    audio_path = request_dir / "Artist - Track.mp3"
    audio_path.write_bytes(b"complete-audio-bytes")

    result = DownloadResult(
        success=True,
        files=[str(audio_path)],
        metadata={"valid": True, "type": "track", "title": "Track", "artist": "Artist"},
        download_dir=str(request_dir),
    )

    monkeypatch.setattr(
        SpotifyDownloader,
        "check_dependencies",
        lambda _self: {"spotdl": True, "ffmpeg": True},
    )
    monkeypatch.setattr(
        SpotifyDownloader,
        "download",
        lambda _self, _url, _user_id, _quality: result,
    )
    monkeypatch.setattr(downloader_module.time, "sleep", lambda _seconds: None)

    bot = Mock()
    uploaded = []

    def send_audio(chat_id, audio_file, **kwargs):
        uploaded.append((chat_id, audio_file.read(), kwargs))
        if len(uploaded) == 1:
            raise TimeoutError("The write operation timed out")
        return object()

    bot.send_audio.side_effect = send_audio
    message = SimpleNamespace(chat=SimpleNamespace(id=-100123456), message_thread_id=None)

    downloader_module.download_and_send(
        bot,
        message,
        SPOTIFY_URL,
        quality=320,
        user_id=987654,
    )

    assert [call[0] for call in uploaded] == [-100123456, -100123456]
    assert [call[1] for call in uploaded] == [
        b"complete-audio-bytes",
        b"complete-audio-bytes",
    ]
    assert uploaded[-1][2]["timeout"] > 0
    assert not request_dir.exists()


def test_telegram_retry_after_is_treated_as_transient():
    error = Exception(
        "A request to the Telegram API was unsuccessful. Error code: 429. "
        "Description: Too Many Requests: retry after 7"
    )

    assert downloader_module._is_retryable_upload_error(error)
    assert downloader_module._upload_retry_delay(error, attempt=1) == 8
