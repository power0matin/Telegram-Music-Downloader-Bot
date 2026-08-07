#!/bin/bash
set -euo pipefail

# Limit cleanup to the dedicated service account instead of killing unrelated
# spotDL/yt-dlp/FFmpeg processes owned by other users on the server.
pkill -TERM -u spotifybot -f 'spotdl|yt-dlp|ffmpeg' || true
