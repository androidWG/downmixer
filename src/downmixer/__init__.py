import argparse
import asyncio
import logging
import os
import shutil
import tempfile
from pathlib import Path

from downmixer.log import setup_logging
from downmixer.file_tools import tag
from downmixer.file_tools import utils
from downmixer.file_tools.convert import Converter
from downmixer.providers import Download, AudioSearchResult
from downmixer.providers.audio.youtube_music import YouTubeMusicAudioProvider
from downmixer.providers.lyrics.azlyrics import AZLyricsProvider
from downmixer.spotify import SpotifyClient

logger = logging.getLogger("downmixer").getChild(__name__)

parser = argparse.ArgumentParser(
    prog="downmixer", description="Easily sync tracks from Spotify."
)
parser.add_argument("procedure", choices=["download"])
parser.add_argument("id")
parser.add_argument("-o", "--output-folder", type=Path, default=os.curdir)
args = parser.parse_args()


spotify = None

ytmusic = None
azlyrics = None


async def _download_and_save_song(result: AudioSearchResult, temp_folder: str):
    downloaded = await ytmusic.download(result, temp_folder)
    converter = Converter(downloaded)
    converted: Download = await converter.convert()

    lyrics_results = await azlyrics.search(converted.song)
    if lyrics_results is not None:
        lyrics = await azlyrics.get_lyrics(lyrics_results[0].url)
        converted.song.lyrics = lyrics
        converted.song.lyrics = lyrics

    tag.tag_download(converted)

    new_name = (
        utils.make_sane_filename(converted.song.title) + converted.filename.suffix
    )
    shutil.move(converted.filename, Path(os.curdir).joinpath(new_name))


async def _get_song(song_id: str):
    song = spotify.song(song_id)

    results = await ytmusic.search(song)
    return results[0]


async def _process_song(temp_folder: str):
    result_song = await _get_song(args.id)
    await _download_and_save_song(result_song, temp_folder)


def command_line():
    setup_logging(debug=True)

    scope = "user-library-read,playlist-read-private"
    global spotify, ytmusic, azlyrics
    spotify = SpotifyClient(scope)

    ytmusic = YouTubeMusicAudioProvider()
    azlyrics = AZLyricsProvider()

    if args.procedure == "download":
        logger.debug("Running download command")
        with tempfile.TemporaryDirectory() as tmp:
            print(f"temp folder: {tmp}")
            asyncio.run(_process_song(tmp))


if __name__ == "__main__":
    command_line()
