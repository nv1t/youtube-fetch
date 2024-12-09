import redis
import json

# Load configuration from JSON file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Redis configuration
REDIS_HOST = config['REDIS_HOST']
REDIS_PORT = config['REDIS_PORT']
REDIS_DB = config['REDIS_DB']
REDIS_PASSWORD = config['REDIS_PASSWORD']
IDS_TO_PROCESS = config['IDS_TO_PROCESS']  # Assuming this is a key in Redis

# Connect to Redis
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

try:
    # Check the length of the lists
    length_ids_to_process = redis_client.llen(IDS_TO_PROCESS)
    print(f"Length of the list '{IDS_TO_PROCESS}': {length_ids_to_process}")

    # Add another list to check
    another_list_key = "ids_processed"  # Replace with the actual list key in Redis
    length_another_list = redis_client.llen(another_list_key)
    print(f"Length of the list '{another_list_key}': {length_another_list}")

except redis.RedisError as e:
    print(f"Redis error: {e}")

