from types import SimpleNamespace
from unittest.mock import Mock

import handlers.callback_handler as callback_handler
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
