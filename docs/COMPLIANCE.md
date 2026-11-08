# Compliance decision: Spotify link preview and audio delivery

**Review date:** 2026-11-08

## Decision

The default operating mode is **Spotify metadata preview only**. The bot may validate a Spotify URL, request the limited information made available through Spotify's official oEmbed endpoint, display a title/creator preview, and link the user directly to the corresponding Spotify item.

The default mode does not search third-party providers for matching audio, download audio, or forward audio files to Telegram.

This decision is based on the current implementation's workflow: it previously used Spotify identifiers and metadata to locate matching audio on other services, then delivered a permanent MP3 copy. Spotify's Developer Terms expressly restrict facilitating stream ripping or permanent copies of Spotify Content. The Spotify Developer Policy also restricts products that integrate Spotify functionality with streams or content from another service. A user submitting a Spotify URL, owning a Spotify subscription, or the project carrying an educational-use disclaimer does not establish permission for that workflow.

## Audio-delivery gate

The optional legacy audio-delivery code is disabled unless the operator explicitly sets:

```dotenv
ENABLE_AUTHORIZED_AUDIO_DELIVERY=true
```

This setting is an **operator attestation only**. It does not grant or verify any permission. Do not enable it unless all of the following have been obtained and reviewed for the exact intended workflow:

1. Written Spotify permission or other documented platform approval covering the proposed use of Spotify metadata/identifiers to identify audio on other services and deliver that audio through this bot. Do not assume that API access or oEmbed access authorizes this integration.
2. Permission under the terms and official download mechanisms of each configured audio provider. Examples:
   - SoundCloud downloads are available only where the uploader has enabled the platform's download feature; this does not by itself authorize redistribution to Telegram recipients.
   - YouTube access and downloads are subject to YouTube's terms, including restrictions on automated access and downloading except where the service, written permission, or applicable law permits it.
   - Bandcamp digital downloads are generally made available through purchases and the account's permitted download flow. A purchase or download does not grant unrestricted redistribution rights.
   - A third-party proxy, mirror, or Piped instance does not create permission to download or redistribute the underlying content.
3. Rights-holder permissions or licences covering reproduction and delivery of every audio file to the intended Telegram recipients, including any commercial use where relevant. Public-domain status or an applicable statutory exception must be established for the relevant work, recording, territory, and use.
4. Review of applicable copyright, consumer, privacy, and platform rules in every jurisdiction where the operator and intended users are located.

The operator is responsible for retaining evidence of these permissions and ensuring that every enabled provider and every delivered file is covered. The application does not inspect licences, determine public-domain status, or provide legal advice. If any required permission is absent, keep the flag set to `false`.

## Spotify metadata, attribution, and artwork

The preview path uses Spotify's official oEmbed endpoint only. It does not scrape Spotify embed-page HTML and does not fetch or display Spotify artwork. Where metadata is available, the preview links directly to the canonical Spotify URL and identifies Spotify as the source. When oEmbed is unavailable, the bot still displays the canonical Spotify link without attempting an HTML-scraping fallback.

This is a limited link-preview use, not a general-purpose metadata or artwork API. Do not store, republish, or combine metadata/artwork beyond what the applicable Spotify documentation and policy permit. If the metadata use or attribution model changes, review the current Spotify policy before release.

## Operational safeguards

- Keep `ENABLE_AUTHORIZED_AUDIO_DELIVERY=false` for ordinary deployments.
- Do not treat a user's request, account subscription, or statement of ownership as platform approval.
- Do not bypass DRM, access controls, geographic restrictions, authentication, rate limits, anti-bot protections, or provider download settings.
- Do not use downloaded files, metadata, or artwork for training, cataloguing, or other secondary uses without a separate rights basis.
- Re-review this decision when providers, features, terms, laws, or deployment jurisdictions change.

## Primary references

- [Spotify Developer Terms of Service](https://developer.spotify.com/terms)
- [Spotify Developer Policy](https://developer.spotify.com/policy)
- [Spotify oEmbed reference](https://developer.spotify.com/documentation/embeds/reference/oembed)
- [SoundCloud Terms of Use](https://soundcloud.com/terms-of-use)
- [SoundCloud: downloading tracks](https://help.soundcloud.com/hc/en-us/articles/115003448807-Downloading-tracks)
- [YouTube Terms of Service](https://www.youtube.com/t/terms)
- [Bandcamp Terms of Use](https://bandcamp.com/terms_of_use)

This document records the project's current technical decision. It is not a legal opinion and does not replace advice from qualified counsel for a particular deployment or jurisdiction.
