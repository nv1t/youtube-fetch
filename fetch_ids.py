import yt_dlp
import logging
import random
import time
import os
import redis
import json

# Load configuration from JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

REDIS_HOST = config.get('REDIS_HOST','localhost')
REDIS_PORT = config.get('REDIS_PORT',6379)
REDIS_DB = config.get('REDIS_DB',0)
REDIS_PASSWORD = config.get('REDIS_PASSWORD',None)
IDS_TO_PROCESS = config.get('IDS_TO_PROCESS','ids_to_process')

# Set the log file name to the script's filename with .log extension
LOG_FILE = os.path.splitext(os.path.basename(__file__))[0] + ".log"

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", filename=LOG_FILE, filemode="w")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
]

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)

def random_delay(min_seconds=1.5, max_seconds=5.0):
    delay = random.uniform(min_seconds, max_seconds)
    logging.info(f"Sleeping for {delay:.2f} seconds")
    time.sleep(delay)

def fetch_channel_data(channel_url):
    ydl_opts = {
        'quiet': True,
        'simulate': True,
        'extract_flat': True,
        'skip_download': True,
        'user_agent': random.choice(USER_AGENTS),
        'noplaylist': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(channel_url, download=False)
            return result
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Failed to fetch data for channel {channel_url}: {e}")
            return None

def save_video_ids_to_redis(channel_url):
    logging.debug(f"Fetching video IDs for channel: {channel_url}")
    channel_data = fetch_channel_data(channel_url)
    if channel_data:
        # Process video entries
        entries = channel_data.get('entries', [])
        for entry in entries:
            video_id = entry.get('id', 'unknown')
            # Push video_id to Redis list
            redis_client.rpush(IDS_TO_PROCESS, video_id)
            logging.info(f"Pushed video ID {video_id} to Redis list '{IDS_TO_PROCESS}'")
    else:
        logging.error(f"Failed to fetch data for channel {channel_url}")

def process_multiple_channels(channel_list):
    total_channels = len(channel_list)
    for i, entry in enumerate(channel_list, start=1):
        category = entry['category']
        channel = entry['channel']
        print(f"Processing channel {i}/{total_channels}: {channel}")
        channel_url = f"https://www.youtube.com/@{channel}/videos"
        save_video_ids_to_redis(channel_url)

def load_channels_from_file(filename):
    try:
        with open(filename, "r") as file:
            channels = json.load(file)
            logging.info(f"Loaded {len(channels)} channels from file.")
            return channels
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Failed to load channels from file: {e}")
        return []

if __name__ == "__main__":
    channels_file = "channels.json"
    channels = load_channels_from_file(channels_file)

    if not channels:
        logging.error("No channels to process. Please check the input file.")
    else:
        process_multiple_channels(channels)
        print("Processing complete. Video IDs have been pushed to Redis.")

