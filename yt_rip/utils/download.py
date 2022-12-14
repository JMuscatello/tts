from typing import List, Dict

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

def preprocess_transcriptions(transcriptions: List[Dict]) -> List[Dict]:
    """Preprocesses list of transcriptions.
    Removes items containing music. Combines transcriptions if less that 1s between them

    Args:
        transcriptions (List[Dict]): List of dictionaries with 'text', 'stat' and 'duration' fields

    Returns:
        List of refined transcription dictionarires in same format as input data
    """

    new_transcriptions = []
    previous_item = None

    def validate_item(item):
        if '[Music]' in item['text']:
            return False
        if len(item['text'].split()) <= 1:
            return False
        if item['duration'] < 1.0:
            return False
        return True

    for item in transcriptions:
        if not validate_item(item):
            print(item['text'])
            if previous_item:
                new_transcriptions.append(previous_item)
                previous_item = None
            continue
        if previous_item:
            # check if current transcription begins > 1s from end of previous
            previous_end = previous_item['start'] + previous_item['duration']
            if item['start'] - previous_end < 0.2:
                previous_item['text'] = previous_item['text'] + ' ' + item['text']
                previous_item['duration'] = (
                    item['start'] - previous_item['start'] + item['duration'])
            else:
                new_transcriptions.append(previous_item)
                previous_item = item

        if not previous_item:
            previous_item = item

    if previous_item and validate_item(previous_item):
        new_transcriptions.append(previous_item)

    return new_transcriptions
