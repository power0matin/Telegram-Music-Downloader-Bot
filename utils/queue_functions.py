"""
Queue management functions for Spotify Bot.

This module handles queue operations with improved error handling and logging.
"""
import json
import os
from typing import List, Dict, Any, Optional

from config import config, QUEUE_PATH
from utils.logging_config import setup_logging

logger = setup_logging(__name__)


def load_queue() -> List[Dict[str, Any]]:
    """
    Load the queue from the JSON file.
    
    Returns:
        List of queue items
    """
    try:
        if not os.path.exists(QUEUE_PATH):
            logger.debug("Queue file does not exist, returning empty queue")
            return []
        
        with open(QUEUE_PATH, "r", encoding='utf-8') as f:
            queue = json.load(f)
            
        logger.debug(f"Loaded queue with {len(queue)} items")
        return queue
        
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading queue: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error loading queue: {e}")
        return []


def save_queue(queue: List[Dict[str, Any]]) -> bool:
    """
    Save the queue to the JSON file.
    
    Args:
        queue: List of queue items
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
        
        with open(QUEUE_PATH, "w", encoding='utf-8') as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Saved queue with {len(queue)} items")
        return True
        
    except Exception as e:
        logger.error(f"Error saving queue: {e}")
        return False


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
        queue = load_queue()
        
        # Check for duplicates
        for item in queue:
            if item.get("link") == link and item.get("user_id") == user_id:
                logger.debug(f"Link already in queue for user {user_id}")
                return False
        
        # Add new item with timestamp
        import time
        new_item = {
            "link": link,
            "user_id": user_id,
            "added_at": time.time()
        }
        
        queue.append(new_item)
        
        if save_queue(queue):
            logger.info(f"Added link to queue for user {user_id}")
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"Error adding to queue: {e}")
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
        queue = load_queue()
        
        # Find first item for this user
        for i, item in enumerate(queue):
            if item.get("user_id") == user_id:
                # Remove item from queue
                removed_item = queue.pop(i)
                
                # Save updated queue
                if save_queue(queue):
                    logger.info(f"Retrieved item from queue for user {user_id}")
                    return removed_item
                else:
                    # If save failed, add item back
                    queue.insert(i, removed_item)
                    return None
        
        logger.debug(f"No queue items found for user {user_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting from queue: {e}")
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
        queue = load_queue()
        original_size = len(queue)
        
        # Remove all items for this user
        queue = [item for item in queue if item.get("user_id") != user_id]
        
        removed_count = original_size - len(queue)
        
        if removed_count > 0:
            if save_queue(queue):
                logger.info(f"Cleared {removed_count} items from queue for user {user_id}")
                return True
        
        return removed_count == 0  # True if nothing to remove
        
    except Exception as e:
        logger.error(f"Error clearing user queue: {e}")
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
        import time
        queue = load_queue()
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        original_size = len(queue)
        
        # Filter out old items
        queue = [
            item for item in queue
            if current_time - item.get("added_at", 0) < max_age_seconds
        ]
        
        cleaned_count = original_size - len(queue)
        
        if cleaned_count > 0:
            if save_queue(queue):
                logger.info(f"Cleaned up {cleaned_count} old queue items")
                return cleaned_count
        
        return 0
        
    except Exception as e:
        logger.error(f"Error cleaning up queue: {e}")
        return 0
