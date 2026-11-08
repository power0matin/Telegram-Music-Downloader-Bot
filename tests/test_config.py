from config import Config, TELEGRAM_AUDIO_SAFE_MAX_BYTES


def test_audio_size_cap_preserves_legacy_mib_configuration(monkeypatch, tmp_path):
    monkeypatch.setenv("DOWNLOAD_DIR", str(tmp_path / "downloads"))
    monkeypatch.setenv("QUEUE_PATH", str(tmp_path / "queue" / "queue.json"))
    monkeypatch.setenv("MAX_DOWNLOAD_SIZE_MB", "50")

    capped = Config.from_env()

    assert capped.max_download_size_mb == 50
    assert capped.max_download_size_bytes == TELEGRAM_AUDIO_SAFE_MAX_BYTES
    assert capped.max_download_size_bytes == 49_000_000

    monkeypatch.setenv("MAX_DOWNLOAD_SIZE_MB", "45")
    custom = Config.from_env()

    assert custom.max_download_size_mb == 45
    assert custom.max_download_size_bytes == 45 * 1024 * 1024
