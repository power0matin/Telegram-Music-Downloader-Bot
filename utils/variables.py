import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_PATH = os.path.join(BASE_DIR, 'queue', 'active_queue.json')
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')

# Ensure directories exist
os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
