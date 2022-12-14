from typing import List

from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi


def get_video_ids_from_playlist(playlist_url: str, only_captions: bool = False) -> List[str]:
    """ Returns list of video ids from playlist, optionally only return urls where captions exists

    Args:
        playlist_url (str): URL of playlist
        only_captions (bool, optional): If true, only return video ids that contain captions

    Returns:
        List of video ids
    """

    with YoutubeDL() as ydl:
        result = ydl.extract_info(playlist_url, download=False)

    video_ids = []

    for entry in result['entries']:
        if only_captions and entry['automatic_captions']:
            video_ids.append(entry['id'])
        elif not only_captions:
            video_ids.append(entry['id'])

    return video_ids
