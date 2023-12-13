import asyncio
import shutil
import tempfile
from pathlib import Path

from spotipy import SpotifyOAuth

import setup_logging
from library import Song
from file_tools import utils
from file_tools import tag
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


async def _process_song(result: ProviderSearchResult, temp_folder: str):
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


async def test_playlist():
    saved_tracks = spotify._saved_tracks()

    with tempfile.TemporaryDirectory() as tmp:
        print(f"temp folder: {tmp}")

        for t in saved_tracks:
            results = await ytmusic.search(t)
            if results is None or len(results) == 0:
                continue

            await _process_song(results[0], tmp)

    print("Done!")


async def test_song():
    song = spotify.song(
        "https://open.spotify.com/track/3VlqU2BNVsIl5MQpNOAbG7?si=d2e3964772f44a30"
    )

    with tempfile.TemporaryDirectory() as tmp:
        print(f"temp folder: {tmp}")

        results = await ytmusic.search(song)
        await _process_song(results[0], tmp)

    print("Done!")


async def test_lyrics():
    song = spotify.song("spotify:track:7gjIVNdtHjbkhH9tfgCPM8")

    results = await azlyrics.search(song)
    lyrics = await azlyrics.get_lyrics(results[0].url)
    print(lyrics)


if __name__ == "__main__":
    setup_logging.setup_logging(debug=True)
    asyncio.run(test_song())
