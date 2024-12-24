# Youtube-fetch Project

This repository documents the journey and implementation of a YouTube scraping toolset designed for collecting video metadata from YouTube channels. Initially relying on the YouTube API, the project evolved to use `yt-dlp` and a distributed scraping system backed by Redis for data storage and TinyDB for persistence. The project also explores sentiment analysis and metadata organization.

## Features
- Fetch channel and video details using the YouTube API.
- Scrape video metadata at scale with `yt-dlp`.
- Distributed scraping setup using Redis to coordinate multiple clients.
- Resilient storage of metadata with TinyDB and disk backups.
- Logging and monitoring for efficient debugging.

---

## Installation
### Prerequisites
1. Python 3.9+
2. Redis server
3. Docker (optional, for running Redis in a container)
4. Dependencies (installed via `pip`):
    - `google-api-python-client`
    - `yt-dlp`
    - `redis`
    - `tinydb`
    - `json`

### Clone the Repository
```bash
git clone https://github.com/yourusername/youtube-fetch.git
cd youtube-fetch
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Project

1. **Set Up the Redis Server**
    - **Option A**: Using Docker:
    ```bash
    docker run --name youtube-redis -p 6379:6379 -d redis
    ```

    - **Option B**: Install Redis locally.
2. **Update your channel list:** Write the channels into a file `channels.json`. Use the sample file as structure
3. **Update the Config**: Update the file `config.json`. A sample file is provided
4. **Fetch Video IDs from Channel and Video Details**
```bash
python fetch_ids.py
```
5. **Get all Video Meta Data**: Run this command on as many PCs as you want.
```bash
python redis_fetch_meta.py
```
6. **Parse the Data**:
```bash
python parse_meta.py
```


## Project Structure
```
youtube-fetch/
|-- fetch_ids.py                # Fetch IDs for channels
|-- parse_meta.py               # Pulls data from Redis and parses it
|-- redis_fetch_meta.py         # fetches an ID from Redis and pulls the meta information
|-- get_video.py                # get a single data information from redis by id
|-- requirements.txt            # Python dependencies
|-- README.md                   # Documentation
```

---

## Important Notes
### Ethical Considerations
This project involves scraping YouTube data, which may violate YouTube's Terms of Service. Use this tool responsibly, respect platform policies, and explore lawful and ethical alternatives.

### Limitations
- YouTube API quota limits.
- IP rate limiting and bot detection during scraping.
- Ensure persistence in Redis for long-running tasks.

---

## Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contact
If you have any questions or suggestions, feel free to reach out via GitHub issues or connect with me directly.

---

## References
- [YouTube API Documentation](https://developers.google.com/youtube/v3)
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)
- [Redis](https://redis.io/)
- [TinyDB](https://tinydb.readthedocs.io/en/latest/)
- [German Sentiment Library](https://github.com/oliverguhr/german-sentiment-lib)
