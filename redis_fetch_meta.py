import redis
import time
import json
import logging
from yt_dlp import YoutubeDL
import os

# Load configuration from JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

REDIS_HOST = config['REDIS_HOST']
REDIS_PORT = config['REDIS_PORT']
REDIS_DB = config['REDIS_DB']
REDIS_PASSWORD = config['REDIS_PASSWORD']
IDS_TO_PROCESS = config['IDS_TO_PROCESS']
IDS_PROCESSED = config['IDS_PROCESSED']

# Set the log file name to the script's filename with .log extension
LOG_FILE = os.path.splitext(os.path.basename(__file__))[0] + ".log"

# Initialize Redis client
if REDIS_PASSWORD:
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,  password=REDIS_PASSWORD, decode_responses=True)
else:
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def fetch_video_metadata(video_id):
    """Fetch metadata for a YouTube video using yt-dlp."""
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True, 'format': 'best', 'dump_single_json': True}
        with YoutubeDL(ydl_opts) as ydl:
            url = f'https://www.youtube.com/watch?v={video_id}'
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        logger.error(f"Error fetching metadata for {video_id}: {e}")
        return None

def main():
    wait_time = 1  # Start with a 1-minute wait time

    while True:
        # Pop an ID from the ids_to_process list
        video_id = redis_client.lpop(IDS_TO_PROCESS)

        if not video_id:
            logger.info("No more IDs to process. Waiting...")
            time.sleep(60)  # Wait before checking again
            continue

        logger.info(f"Processing video ID: {video_id}")
        metadata = fetch_video_metadata(video_id)

        if metadata is None:
            logger.warning(f"Failed to fetch metadata for {video_id}. Waiting {wait_time} minutes before retrying.")
            time.sleep(wait_time * 60)
            wait_time += 2  # Increment wait time
            redis_client.rpush(IDS_TO_PROCESS, video_id)  # Re-add to the processing list
            continue

        # Reset wait time on success
        wait_time = 1

        # Save metadata to Redis
        redis_client.set(f"{video_id}:metainformation", json.dumps(metadata))
        logger.info(f"Saved metadata for {video_id}")

        # Push the video ID to the processed list
        redis_client.rpush(IDS_PROCESSED, video_id)
        logger.info(f"Added {video_id} to processed list")

if __name__ == "__main__":
    main()
