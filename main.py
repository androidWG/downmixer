import asyncio
import shutil
import tempfile
from pathlib import Path

from spotipy import SpotifyOAuth

import file_tools.convert
import setup_logging
from file_tools.tagging import tag_download
from file_tools.utils import make_sane_filename
from library import Song
from providers import Download
from providers.audio.youtube_music import YouTubeMusicAudioProvider
from spotify import SpotipyClient

scope = "user-library-read,playlist-read-private"
spotify = SpotipyClient(auth_manager=SpotifyOAuth(scope=scope))

folder = Path(r"D:\Files\Music")
provider = YouTubeMusicAudioProvider()


def test_playlist():
    saved_tracks = spotify.current_user_saved_tracks_processed()

    with tempfile.TemporaryDirectory() as tmp:
        for t in saved_tracks:
            results = provider.search(t)
            if results is None or len(results) == 0:
                continue

            print(f"temp folder: {tmp}")

            downloaded = provider.download(results[0], tmp)
            converted: Download = asyncio.run(
                file_tools.convert.convert_download(downloaded)
            )
            tag_download(converted)

            new_name = (
                make_sane_filename(converted.search_result.result_song.title)
                + converted.filename.suffix
            )
            shutil.move(converted.filename, "D:\\Files\\Music\\" + new_name)

            print("Done!")


def test_song():
    sp_result = spotify.track("https://open.spotify.com/track/1BnODvOuKbTnAZYkMVzJCL")
    song = Song.from_spotify(sp_result)

    results = provider.search(song)
    downloaded = provider.download(results[0], folder)
    converted = asyncio.run(file_tools.convert.convert_download(downloaded))
    tag_download(converted)
    print("Done!")


if __name__ == "__main__":
    setup_logging.setup_logging(debug=True)
    test_playlist()
