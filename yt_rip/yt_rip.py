import click

from utils.download import download_audio_from_playlist  


@click.command()
@click.option('--playlist_id', help='ID of YouTube playlist', required=True)
@click.option('-o', '--output', help='Output directory to download files and metadata', required=True)
@click.option('--overwrite_metadata', default=False, help='If True, create new metadata file')
def download(playlist_id, output, overwrite_metadata):
    """Downloads audio from all videos in given playlist where captions are available.
    Audio is split into separate files in directory structure used by Tacotron 2 example
    training script provided by nvidia.
    """

    playlist_url = f'https://youtube.com/playlist?list={playlist_id}'

    download_audio_from_playlist(playlist_url, output, overwrite_metadata)


if __name__ == '__main__':
    download()    
