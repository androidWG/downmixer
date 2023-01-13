import asyncio
import shutil
import tempfile
from pathlib import Path

from spotipy import SpotifyOAuth

import file_tools.convert
import setup_logging
import file_tools.tagging
import file_tools.utils
from library import Song
from providers import Download, ProviderSearchResult
from providers.audio.youtube_music import YouTubeMusicAudioProvider
from providers.lyrics.azlyrics import AZLyricsProvider
from spotify import SpotipyClient

scope = "user-library-read,playlist-read-private"
spotify = SpotipyClient(auth_manager=SpotifyOAuth(scope=scope))

folder = Path(r"D:\Files\Music")
ytmusic = YouTubeMusicAudioProvider()
azlyrics = AZLyricsProvider()


def _process_song(result: ProviderSearchResult, temp_folder: str):
    downloaded = ytmusic.download(result, temp_folder)
    converted: Download = asyncio.run(file_tools.convert.convert_download(downloaded))

    lyrics_results = azlyrics.search(converted.search_result.result_song)
    lyrics = azlyrics.get_lyrics(lyrics_results[0].result_song.url)
    converted.search_result.result_song.lyrics = lyrics
    converted.search_result.original_song.lyrics = lyrics

    file_tools.tagging.tag_download(converted)

    new_name = (
        file_tools.utils.make_sane_filename(converted.search_result.result_song.title)
        + converted.filename.suffix
    )
    shutil.move(converted.filename, "D:\\Files\\Music\\" + new_name)


def test_playlist():
    saved_tracks = spotify.current_user_saved_tracks_processed()

    with tempfile.TemporaryDirectory() as tmp:
        print(f"temp folder: {tmp}")

        for t in saved_tracks:
            results = ytmusic.search(t)
            if results is None or len(results) == 0:
                continue

            _process_song(results[0], tmp)

    print("Done!")


def test_song():
    sp_result = spotify.track("https://open.spotify.com/track/3VlqU2BNVsIl5MQpNOAbG7?si=d2e3964772f44a30")
    song = Song.from_spotify(sp_result)

    with tempfile.TemporaryDirectory() as tmp:
        print(f"temp folder: {tmp}")

        results = ytmusic.search(song)
        _process_song(results[0], tmp)

    print("Done!")


def test_lyrics():
    sp_result = spotify.track("spotify:track:7gjIVNdtHjbkhH9tfgCPM8")
    song = Song.from_spotify(sp_result)

    results = azlyrics.search(song)
    lyrics = azlyrics.get_lyrics(results[0].result_song.url)
    print(lyrics)


if __name__ == "__main__":
    setup_logging.setup_logging(debug=True)
    test_song()
