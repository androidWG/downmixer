import argparse
import asyncio
import os
import pathlib
import shutil
import tempfile
from pathlib import Path

import setup_logging
from file_tools import tag
from file_tools import utils
from file_tools.convert import Converter
from providers import Download, ProviderSearchResult
from providers.audio.youtube_music import YouTubeMusicAudioProvider
from providers.lyrics.azlyrics import AZLyricsProvider
from spotify import SpotipyClient

scope = "user-library-read,playlist-read-private"
spotify = SpotipyClient(scope)

folder = Path(r"D:\Files\Music")
ytmusic = YouTubeMusicAudioProvider()
azlyrics = AZLyricsProvider()

parser = argparse.ArgumentParser(
    prog="downmixer", description="Easily sync tracks from Spotify."
)
parser.add_argument("procedure", choices=["download"])
parser.add_argument("id")
parser.add_argument("-o", "--output-folder", type=pathlib.Path, default=os.curdir)
args = parser.parse_args()


async def _download_and_save_song(result: ProviderSearchResult, temp_folder: str):
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
    shutil.move(converted.filename, "D:\\Files\\Music\\" + new_name)


async def _get_song(song_id: str):
    song = spotify.song(song_id)

    results = await ytmusic.search(song)
    return results[0]


async def _process_song(temp_folder: str):
    result_song = await _get_song(args.id)
    await _download_and_save_song(result_song, temp_folder)


if __name__ == "__main__":
    setup_logging.setup_logging(debug=True)

    if args.procedure == "download":
        with tempfile.TemporaryDirectory() as tmp:
            print(f"temp folder: {tmp}")
            asyncio.run(_process_song(tmp))
