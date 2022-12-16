from typing import List, Dict

from math import ceil

import librosa
import soundfile as sf

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


def download_audio_from_transcriptions(
    video_id: str,
    transcriptions: List[Dict],
    output_dir: str,
    sample_rate: int = 22050,
) -> (List[str], List[str]):
    """Download each item in the transcription list as separate audio files.
    Downloads audio of entire video then splits using librosa

    Args:
        video_id (str): youtube video id
        transcriptions (List[Dict]): List of dictionaries containing transcription data
        output_dir (str): Output directory
        sample_rate (int): sample rate for audio conversion

    Returns:
        List of (text, filename) tuples
    """
    url = f'https://www.youtube.com/watch?v={video_id}'

    for idx, item in enumerate(transcriptions):
        start = item['start']
        end = start + item['duration']
        text = item['text']

    # download audio
    ydl_opts = {
        'outtmpl': f"{output_dir}/{video_id}_audio.%(ext)s",
        'format': 'm4a/bestaudio/best',
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'postprocessor_args': [
            '-ar', str(sample_rate),
            '-ac', '1',
            '-acodec', 'pcm_s16le',
            '-f', 'WAV',
        ],
        'prefer_ffmpeg': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

    root_filename = f"{output_dir}/{video_id}_audio.wav"
    audio, sample_rate = librosa.load(root_filename)

    annotations = []
    filenames = []
    for idx, item in enumerate(transcriptions):
        start = item['start']
        end = start + item['duration']
        text = item['text']

        start_index = ceil(sample_rate*start)
        end_index = ceil(sample_rate*end)
        filename = f"{output_dir}/{video_id}_{idx+1:04}.wav"
        sf.write(
            filename,
            audio[start_index:end_index],
            sample_rate
        )

        annotations.append(text)
        filenames.append(filename)

    return annotations, filenames
