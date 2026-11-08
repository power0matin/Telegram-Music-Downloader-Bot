from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import Mock

import handlers.callback_handler as callback_handler
import handlers.spotify_handler as spotify_handler
from handlers.spotify_handler import LinkStore, format_metadata_html


def test_link_store_callback_can_only_be_consumed_once():
    store = LinkStore(expiry_seconds=60)
    store.store_link("abc", "https://open.spotify.com/track/123", 42)

    assert store.consume_link("abc", 42) is not None
    assert store.consume_link("abc", 42) is None


def test_link_store_does_not_leak_link_to_another_user():
    store = LinkStore(expiry_seconds=60)
    store.store_link("abc", "https://open.spotify.com/track/123", 42)

    assert store.consume_link("abc", 99) is None
    assert store.consume_link("abc", 42) is not None


def test_link_store_survives_reopen_and_preserves_metadata(tmp_path):
    db_path = tmp_path / "pending_links.sqlite3"
    first_store = LinkStore(expiry_seconds=60, db_path=db_path)
    metadata = {"valid": True, "title": "Track", "artist": "Artist"}
    first_store.store_link(
        "restart-safe",
        "https://open.spotify.com/track/123",
        42,
        metadata,
    )

    reopened_store = LinkStore(expiry_seconds=60, db_path=db_path)

    assert reopened_store.retrieve_link("restart-safe", 42)["metadata"] == metadata
    consumed = reopened_store.consume_link("restart-safe", 42)
    assert consumed["link"] == "https://open.spotify.com/track/123"
    assert consumed["metadata"] == metadata
    assert first_store.consume_link("restart-safe", 42) is None


def test_link_store_rejects_expired_link_after_reopen(monkeypatch, tmp_path):
    clock = [1000.0]
    monkeypatch.setattr("handlers.spotify_handler.time.time", lambda: clock[0])
    db_path = tmp_path / "pending_links.sqlite3"
    store = LinkStore(expiry_seconds=10, db_path=db_path)
    store.store_link("expired", "https://open.spotify.com/track/123", 42)

    clock[0] = 1011.0
    reopened_store = LinkStore(expiry_seconds=10, db_path=db_path)

    assert reopened_store.retrieve_link("expired", 42) is None
    assert reopened_store.consume_link("expired", 42) is None


def test_link_store_expiry_boundary_remains_valid_at_exact_ttl(
    monkeypatch, tmp_path
):
    clock = [1000.0]
    monkeypatch.setattr("handlers.spotify_handler.time.time", lambda: clock[0])
    store = LinkStore(
        expiry_seconds=10,
        db_path=tmp_path / "pending_links.sqlite3",
    )
    store.store_link("boundary", "https://open.spotify.com/track/123", 42)

    clock[0] = 1010.0

    assert store.retrieve_link("boundary", 42) is not None


def test_link_store_consumption_is_atomic_across_instances(tmp_path):
    db_path = tmp_path / "pending_links.sqlite3"
    stores = [
        LinkStore(expiry_seconds=60, db_path=db_path)
        for _ in range(12)
    ]
    stores[0].store_link(
        "atomic",
        "https://open.spotify.com/track/123",
        42,
        {"title": "Track"},
    )

    with ThreadPoolExecutor(max_workers=len(stores)) as executor:
        results = list(
            executor.map(lambda store: store.consume_link("atomic", 42), stores)
        )

    consumed = [result for result in results if result is not None]
    assert len(consumed) == 1
    assert consumed[0]["metadata"] == {"title": "Track"}


def test_metadata_html_escapes_spotify_text():
    text = format_metadata_html(
        {
            "valid": True,
            "title": "A <Track> & More",
            "artist": "Artist <script>",
        }
    )

    assert "<b>A &lt;Track&gt; &amp; More</b>" in text
    assert "Artist &lt;script&gt;" in text
    assert "<script>" not in text


def test_spotify_message_defaults_to_metadata_preview_without_quality_keyboard(
    monkeypatch
):
    class FakeBot:
        def __init__(self):
            self.message_handlers = []
            self.replies = []

        def message_handler(self, **_kwargs):
            def decorator(handler):
                self.message_handlers.append(handler)
                return handler
            return decorator

        def reply_to(self, message, text, **kwargs):
            self.replies.append((message, text, kwargs))

    bot = FakeBot()
    monkeypatch.setattr(
        spotify_handler,
        "config",
        SimpleNamespace(enable_authorized_audio_delivery=False),
    )
    monkeypatch.setattr(
        spotify_handler, "check_rate_limit", lambda _user_id: (True, 0)
    )
    monkeypatch.setattr(
        spotify_handler, "sanitize_spotify_url", lambda url: url
    )
    monkeypatch.setattr(
        spotify_handler, "validate_spotify_url", lambda _url: True
    )
    spotify_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
    monkeypatch.setattr(
        spotify_handler, "get_canonical_spotify_url", lambda _url: spotify_url
    )
    monkeypatch.setattr(
        spotify_handler,
        "get_spotify_metadata",
        lambda _url: {
            "valid": True,
            "type": "track",
            "title": "Track",
            "artist": "Artist",
            "url": spotify_url,
            "external_urls": {"spotify": spotify_url},
        },
    )
    store_link = Mock()
    add_to_queue = Mock()
    monkeypatch.setattr(spotify_handler.link_store, "store_link", store_link)
    monkeypatch.setattr(spotify_handler, "add_to_queue", add_to_queue)

    spotify_handler.register_spotify_handler(bot)
    handler = bot.message_handlers[0]
    message = SimpleNamespace(
        from_user=SimpleNamespace(id=42),
        chat=SimpleNamespace(id=42),
        text=spotify_url,
    )

    handler(message)

    assert len(bot.replies) == 1
    _, reply_text, kwargs = bot.replies[0]
    assert "Track" in reply_text
    assert spotify_url in reply_text
    assert "reply_markup" not in kwargs
    assert kwargs["parse_mode"] == "HTML"
    store_link.assert_not_called()
    add_to_queue.assert_not_called()


def test_disabled_audio_delivery_rejects_existing_quality_callback(monkeypatch):
    class FakeBot:
        def __init__(self):
            self.callback_handlers = []
            self.answers = []

        def callback_query_handler(self, **_kwargs):
            def decorator(handler):
                self.callback_handlers.append(handler)
                return handler
            return decorator

        def answer_callback_query(self, callback_id, text):
            self.answers.append((callback_id, text))

    bot = FakeBot()
    monkeypatch.setattr(
        callback_handler,
        "config",
        SimpleNamespace(enable_authorized_audio_delivery=False),
    )
    get_link = Mock()
    consume_link = Mock()
    monkeypatch.setattr(callback_handler, "get_stored_link_data", get_link)
    monkeypatch.setattr(callback_handler, "consume_stored_link_data", consume_link)
    download = Mock()
    monkeypatch.setattr(callback_handler, "download_and_send", download)

    callback_handler.register_callback_handlers(bot)
    handler = next(
        item for item in bot.callback_handlers
        if item.__name__ == "handle_quality_selection"
    )
    call = SimpleNamespace(
        id="callback-id",
        data="quality|320|abc123",
        from_user=SimpleNamespace(id=42),
        message=SimpleNamespace(
            chat=SimpleNamespace(id=123),
            message_id=55,
        ),
    )

    handler(call)

    assert len(bot.answers) == 1
    assert bot.answers[0][0] == "callback-id"
    get_link.assert_not_called()
    consume_link.assert_not_called()
    download.assert_not_called()


def test_metadata_preview_always_contains_attributed_spotify_link():
    spotify_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
    text = format_metadata_html(
        {
            "valid": False,
            "url": spotify_url,
            "external_urls": {"spotify": spotify_url},
        },
        link_label="Open on Spotify",
    )

    assert f'href="{spotify_url}"' in text
    assert "Open on Spotify" in text


def test_status_message_failures_do_not_block_download(monkeypatch):
    """Transient Telegram UI failures must not consume a link without delivery."""

    class ImmediateThread:
        def __init__(self, target, daemon=False):
            self.target = target

        def start(self):
            self.target()

    class FakeBot:
        def __init__(self):
            self.callback_handlers = []

        def callback_query_handler(self, **_kwargs):
            def decorator(func):
                self.callback_handlers.append(func)
                return func

            return decorator

        def answer_callback_query(self, *_args, **_kwargs):
            raise TimeoutError("Telegram acknowledgement timed out")

        def edit_message_text(self, **_kwargs):
            raise TimeoutError("Telegram edit timed out")

        def send_message(self, *_args, **_kwargs):
            raise TimeoutError("Telegram status send timed out")

    download = Mock()
    monkeypatch.setattr(
        callback_handler,
        "config",
        SimpleNamespace(enable_authorized_audio_delivery=True),
    )
    monkeypatch.setattr(callback_handler, "download_and_send", download)
    link_data = {
        "link": "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
        "metadata": {},
    }
    monkeypatch.setattr(
        callback_handler,
        "get_stored_link_data",
        lambda _link_id, _user_id: link_data,
    )
    monkeypatch.setattr(
        callback_handler,
        "consume_stored_link_data",
        lambda _link_id, _user_id: link_data,
    )
    monkeypatch.setattr(callback_handler, "validate_spotify_url", lambda _url: True)
    monkeypatch.setattr(callback_handler.threading, "Thread", ImmediateThread)

    bot = FakeBot()
    callback_handler.register_callback_handlers(bot)
    quality_handler = next(
        handler
        for handler in bot.callback_handlers
        if handler.__name__ == "handle_quality_selection"
    )

    message = SimpleNamespace(
        chat=SimpleNamespace(id=-100123),
        message_id=55,
        message_thread_id=12,
    )
    call = SimpleNamespace(
        id="callback-id",
        data="quality|320|abc123",
        from_user=SimpleNamespace(id=42),
        message=message,
    )

    quality_handler(call)

    download.assert_called_once_with(
        bot,
        message,
        "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
        320,
        user_id=42,
    )
