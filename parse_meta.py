import hashlib
import redis
import json
import logging
import os
from tqdm import tqdm
from tinydb import TinyDB, where

# Function to encode video ID using SHA256
def encode_video_id_hash(video_id):
    return hashlib.sha256(video_id.encode()).hexdigest()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

REDIS_HOST = config['REDIS_HOST']
REDIS_PORT = config['REDIS_PORT']
REDIS_DB = config['REDIS_DB']
REDIS_PASSWORD = config.get('REDIS_PASSWORD')  # Optional
IDS_PROCESSED = config['IDS_PROCESSED']
TINYDB_FILE = config.get('TINYDB_FILE', 'video_metadata.json')  # Default to 'video_metadata.json'
OUTPUT_DIR = config.get('OUTPUT_DIR', 'output_metadata')  # Default directory for raw JSON files

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Connect to the Redis server
try:
    redis_client = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        decode_responses=True  # Automatically decode bytes to str
    )
    logging.info("Connected to Redis server.")
except redis.ConnectionError as e:
    logging.error("Failed to connect to Redis server: %s", e)
    exit(1)

# Connect to TinyDB
db = TinyDB(TINYDB_FILE)
video_table = db.table('videos')

# Fetch and process video IDs from Redis stack
logging.info(f"Starting to process video IDs from {IDS_PROCESSED}.")
while True:
    video_id = redis_client.rpop(IDS_PROCESSED)  # Pop the last ID from the list
    if not video_id:
        logging.info("No more video IDs left to process.")
        break

    metadata_key = f"{video_id}:metainformation"
    metadata_json = redis_client.get(metadata_key)

    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
            metadata_video = {
                'id': video_id,
                'title': metadata.get('title'),
                'description': metadata.get('description'),
                'duration': metadata.get('duration'),
                'like_count': metadata.get('like_count'),
                'view_count': metadata.get('view_count'),
                'channel': metadata.get('channel'),
                'channel_id': metadata.get('channel_id'),
                'timestamp': metadata.get('timestamp'),
            }

            # Hash video_id for the file name
            hashed_video_id = encode_video_id_hash(video_id)

            # Write raw metadata to a file
            output_file = os.path.join(OUTPUT_DIR, f"{hashed_video_id}.json")
            with open(output_file, 'w') as f:
                f.write(metadata_json)
            logging.info(f"Raw metadata for video ID {video_id} written to {output_file}.")

            # Insert metadata into TinyDB
            video_table.upsert(metadata_video, where('id') == video_id)
            logging.info(f"Processed and stored metadata for video ID {video_id}.")
        except json.JSONDecodeError as e:
            logging.warning("Failed to decode metadata for video ID %s: %s", video_id, e)
    else:
        logging.warning("No metadata found for video ID %s", video_id)

logging.info(f"All video IDs processed. Raw metadata stored in {OUTPUT_DIR} and processed data in {TINYDB_FILE}.")
