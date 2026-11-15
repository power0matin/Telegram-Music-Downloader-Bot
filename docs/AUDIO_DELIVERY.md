# Authorized audio-delivery operations

**Default state: disabled.** The bot normally previews Spotify links and does not search for, download, or deliver audio.

The optional workflow is implemented in the repository: it passes a validated Spotify URL to spotDL, attempts to resolve matching recordings through the configured `AUDIO_PROVIDERS`, processes the resulting local audio files, and uploads eligible files with Telegram `send_audio`. It does **not** download audio from Spotify's audio service. Provider matches may be unavailable, may represent a different recording/master, and album or playlist delivery may be partial.

This workflow is only for deployments that already hold written platform permissions and rights-holder licences for the exact use. It is not a way to bypass DRM or provider restrictions.

## Authorization

Before enabling the feature, retain evidence covering:
- Spotify permission for using Spotify links/metadata to identify recordings on other services.
- Permission under each configured provider's terms and official download mechanism.
- Rights-holder licences for reproducing and delivering every recording to Telegram recipients.
- Applicable territorial, commercial, privacy, and platform requirements.

A public URL, accessible provider result, Spotify subscription, or purchase does not by itself establish redistribution rights. Do not bypass DRM, provider download controls, login requirements, geographic restrictions, rate limits, or anti-bot controls. See [COMPLIANCE.md](COMPLIANCE.md).

## Explicit opt-in

Only after obtaining the required permissions, set both values in `.env`:

```dotenv
ENABLE_AUTHORIZED_AUDIO_DELIVERY=true
AUDIO_DELIVERY_PERMISSIONS_ACK=true
```

The second value is an operator acknowledgement only. It is not verified by the application and grants no permission. The application refuses to start the audio path if the first flag is true and the acknowledgement is absent or false. Keep both false for ordinary deployments.

Configure only authorized sources:

```dotenv
AUDIO_PROVIDERS=soundcloud,youtube-music,youtube
SPOTDL_EXECUTABLE=
```

Optional connectivity settings include `PROXY_URL`, `COOKIE_FILE`, and `YTDLP_EXTRA_ARGS`. Cookies are sensitive credentials: keep them private and never use them to bypass provider restrictions.

## Runtime requirements

- Python 3.11–3.15.
- spotDL 4.6.0, installed in the same virtual environment as the bot.
- FFmpeg available on `PATH`.
- Telegram bot token and network access to the permitted providers.

The bot resolves spotDL beside the active Python interpreter first, then falls back to `PATH`. `SPOTDL_EXECUTABLE` can override the path.

## Delivery flow and limits

1. The user sends a Spotify Track, Album, or Playlist URL.
2. The bot validates the URL and fetches limited metadata using Spotify oEmbed.
3. The user selects 128 or 320 kbps.
4. spotDL resolves items from configured sources and writes them to an isolated request directory.
5. The bot validates output type, non-empty content, and size, then sends each accepted file using Telegram `send_audio`.
6. Partial failures are reported and temporary request files are removed.

The hosted Bot API upload ceiling is conservatively capped at 49,000,000 bytes per file. Larger files are skipped; album and playlist results can therefore be partial. The bot cannot guarantee a matching source or identical master recording, nor that a provider remains available. Technical success is not evidence of permission.

## VPS notes

The systemd unit adds the virtual environment's `bin` directory to `PATH`. After changing configuration:

```bash
sudo systemctl restart spotify-bot
sudo systemctl status spotify-bot
sudo journalctl -u spotify-bot -n 100 --no-pager
```

Never paste tokens, cookies, proxy credentials, or full environment files into logs or support requests.

## Validation

```bash
python -m compileall -q bot.py config.py handlers utils tests
pytest -q
bash -n setup_vps.sh start_bot.sh scripts/*.sh
```

CI uses mocked provider/download behavior. It does not perform live media downloads or prove that a source is reachable from a particular VPS.

To disable the feature again, set both flags to false and restart the bot.
