"""
Queue management functions for Spotify Bot.

This module handles queue operations with improved error handling and logging.
"""

import json
import os
import tempfile
import time
from threading import RLock
from typing import List, Dict, Any, Optional

from config import config, QUEUE_PATH
from utils.logging_config import setup_logging

logger = setup_logging(__name__)
_queue_lock = RLock()


def load_queue() -> List[Dict[str, Any]]:
    """
    Load the queue from the JSON file.

    Returns:
        List of queue items
    """
    try:
        with _queue_lock:
            if not os.path.exists(QUEUE_PATH):
                logger.debug("Queue file does not exist, returning empty queue")
                return []

            with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                queue = json.load(f)

            if not isinstance(queue, list):
                logger.error("Queue file does not contain a JSON list; ignoring it")
                return []

            logger.debug("Loaded queue with %d items", len(queue))
            return queue

    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error("Error loading queue: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error loading queue: %s", e)
        return []


def save_queue(queue: List[Dict[str, Any]]) -> bool:
    """
    Save the queue to the JSON file.

    Args:
        queue: List of queue items

    Returns:
        True if successful, False otherwise
    """
    temp_path: Optional[str] = None
    try:
        with _queue_lock:
            queue_dir = os.path.dirname(QUEUE_PATH) or "."
            os.makedirs(queue_dir, exist_ok=True)

            fd, temp_path = tempfile.mkstemp(prefix=".queue-", dir=queue_dir)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(queue, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, QUEUE_PATH)
            temp_path = None
            logger.debug("Saved queue with %d items", len(queue))
            return True

    except Exception as e:
        logger.error("Error saving queue: %s", e)
        return False
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def add_to_queue(link: str, user_id: int) -> bool:
    """
    Add a link and user ID to the queue if not already present.

    Args:
        link: Spotify link
        user_id: Telegram user/chat ID

    Returns:
        True if added, False if already exists or error
    """
    try:
        with _queue_lock:
            queue = load_queue()

            # Check for duplicates
            for item in queue:
                if item.get("link") == link and item.get("user_id") == user_id:
                    logger.debug("Link already in queue for user %s", user_id)
                    return False

            # Add new item with timestamp
            new_item = {"link": link, "user_id": user_id, "added_at": time.time()}

            queue.append(new_item)

            if save_queue(queue):
                logger.info("Added link to queue for user %s", user_id)
                return True
            return False

    except Exception as e:
        logger.error("Error adding to queue: %s", e)
        return False


def get_next_from_queue(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the next item for a user from the queue.

    Args:
        user_id: Telegram user/chat ID

    Returns:
        Queue item or None if not found
    """
    try:
        with _queue_lock:
            queue = load_queue()

            # Find first item for this user
            for i, item in enumerate(queue):
                if item.get("user_id") == user_id:
                    removed_item = queue.pop(i)

                    if save_queue(queue):
                        logger.info("Retrieved item from queue for user %s", user_id)
                        return removed_item

                    queue.insert(i, removed_item)
                    return None

            logger.debug("No queue items found for user %s", user_id)
            return None

    except Exception as e:
        logger.error("Error getting from queue: %s", e)
        return None


def get_queue_size() -> int:
    """
    Get the total number of items in the queue.

    Returns:
        Number of items in queue
    """
    try:
        queue = load_queue()
        return len(queue)
    except Exception:
        return 0


def get_user_queue_size(user_id: int) -> int:
    """
    Get the number of items in queue for a specific user.

    Args:
        user_id: Telegram user/chat ID

    Returns:
        Number of items in queue for user
    """
    try:
        queue = load_queue()
        return sum(1 for item in queue if item.get("user_id") == user_id)
    except Exception:
        return 0


def clear_user_queue(user_id: int) -> bool:
    """
    Clear all queue items for a specific user.

    Args:
        user_id: Telegram user/chat ID

    Returns:
        True if successful
    """
    try:
        with _queue_lock:
            queue = load_queue()
            original_size = len(queue)

            queue = [item for item in queue if item.get("user_id") != user_id]

            removed_count = original_size - len(queue)

            if removed_count > 0:
                if save_queue(queue):
                    logger.info(
                        "Cleared %d items from queue for user %s", removed_count, user_id
                    )
                    return True

            return removed_count == 0

    except Exception as e:
        logger.error("Error clearing user queue: %s", e)
        return False


def cleanup_old_queue_items(max_age_hours: int = 24) -> int:
    """
    Clean up old queue items.

    Args:
        max_age_hours: Maximum age in hours before cleanup

    Returns:
        Number of items cleaned up
    """
    try:
        with _queue_lock:
            queue = load_queue()
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            original_size = len(queue)

            queue = [
                item
                for item in queue
                if current_time - item.get("added_at", 0) < max_age_seconds
            ]

            cleaned_count = original_size - len(queue)

            if cleaned_count > 0:
                if save_queue(queue):
                    logger.info("Cleaned up %d old queue items", cleaned_count)
                    return cleaned_count

            return 0

    except Exception as e:
        logger.error("Error cleaning up queue: %s", e)
        return 0
