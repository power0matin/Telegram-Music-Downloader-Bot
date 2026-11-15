from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_systemd_unit_exposes_virtualenv_cli_tools_on_path():
    service = (ROOT / "systemd" / "spotify-bot.service").read_text(encoding="utf-8")
    assert 'Environment="PATH=/opt/Telegram-Music-Downloader-Bot/venv/bin:' in service


def test_vps_installer_uses_safe_audio_defaults_and_avoids_full_os_upgrade():
    installer = (ROOT / "setup_vps.sh").read_text(encoding="utf-8")
    assert "ENABLE_AUTHORIZED_AUDIO_DELIVERY=false" in installer
    assert "AUDIO_DELIVERY_PERMISSIONS_ACK=false" in installer
    assert "apt-get upgrade" not in installer
    assert "sys.version_info[:2] < (3, 16)" in installer
