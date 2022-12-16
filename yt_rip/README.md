# yt-rip
Script for extracting audio data from YouTube playlists

## Installation
Install dependencies to a virtual environment
```
$ python -m venv .env
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

## Usage
Run the script with a YouTube playlist ID and location of output. New files will be added to any existing metadata unless `--overwrite_metadata` is supplied.
```
$ python yt_rip --playlist_id LNR9e5gIAR0ep6TiEuqNJB_I1ohTZ4bg_ -o .data
```

