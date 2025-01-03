import redis
import json
import sys

# Load configuration from JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

REDIS_HOST = config.get('REDIS_HOST','localhost')
REDIS_PORT = config.get('REDIS_PORT',6379)
REDIS_DB = config.get('REDIS_DB',0)
REDIS_PASSWORD = config.get('REDIS_PASSWORD',None)

# Connect to Redis
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

try:
    # Ensure a video ID is passed as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python script.py <video_id>")
        sys.exit(1)

    # Construct the key using the format string
    video_id_key = f"{sys.argv[1]}:metainformation"

    # Retrieve the value
    video_data = redis_client.get(video_id_key)

    # Output the value
    if video_data is not None:
        print(f"{video_data}")
    else:
        print(f"No value found for key '{video_id_key}'.")

except redis.RedisError as e:
    print(f"Redis error: {e}")
except Exception as ex:
    print(f"An error occurred: {ex}")

