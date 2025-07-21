import json
from utils.variables import QUEUE_PATH

def load_queue():
    try:
        with open(QUEUE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_queue(queue):
    with open(QUEUE_PATH, 'w') as f:
        json.dump(queue, f, indent=2)

def add_to_queue(link, user_id):
    queue = load_queue()
    queue.append({"link": link, "user_id": user_id})
    save_queue(queue)
