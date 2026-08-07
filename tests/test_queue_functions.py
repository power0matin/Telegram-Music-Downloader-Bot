from concurrent.futures import ThreadPoolExecutor

import utils.queue_functions as queue_functions


def test_concurrent_queue_writes_are_not_lost(monkeypatch, tmp_path):
    queue_path = tmp_path / "queue.json"
    monkeypatch.setattr(queue_functions, "QUEUE_PATH", str(queue_path))

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(
            executor.map(
                lambda i: queue_functions.add_to_queue(
                    f"https://open.spotify.com/track/{i:022d}", i
                ),
                range(30),
            )
        )

    assert all(results)
    queue = queue_functions.load_queue()
    assert len(queue) == 30
    assert {item["user_id"] for item in queue} == set(range(30))
