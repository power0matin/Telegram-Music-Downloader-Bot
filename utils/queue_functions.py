import json
import os
from utils.variables import QUEUE_PATH


def load_queue():
    """Load the queue from the JSON file."""
    try:
        if not os.path.exists(QUEUE_PATH):
            return []
        with open(QUEUE_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading queue: {e}")
        return []


def save_queue(queue):
    """Save the queue to the JSON file."""
    try:
        os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
        with open(QUEUE_PATH, "w") as f:
            json.dump(queue, f, indent=2)
    except Exception as e:
        print(f"Error saving queue: {e}")


def add_to_queue(link: str, user_id: int):
    """Add a link and user ID to the queue if not already present."""
    queue = load_queue()
    # Check for duplicates
    if any(item["link"] == link and item["user_id"] == user_id for item in queue):
        return False  # Link already in queue
    queue.append({"link": link, "user_id": user_id})
    save_queue(queue)
    return True


def get_next_from_queue(user_id: int):
    """Get the next item for a user from the queue."""
    queue = load_queue()
    for item in queue:
        if item["user_id"] == user_id:
            queue.remove(item)
            save_queue(queue)
            return item
    return None
