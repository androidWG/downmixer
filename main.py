import asyncio
from pathlib import Path

from spotipy import SpotifyOAuth

import downloader.convert
from library import Song
from providers.audio.youtube_music import YouTubeMusicAudioProvider
from spotify import SpotipyClient

scope = "user-library-read,playlist-read-private"
spotify = SpotipyClient(auth_manager=SpotifyOAuth(scope=scope))

folder = Path(r"D:\Files\Music")
provider = YouTubeMusicAudioProvider()


def test_playlist():
    saved_tracks = spotify.current_user_saved_tracks_processed()

    for t in saved_tracks:
        results = provider.search(t)
        if results is None or len(results) == 0:
            continue

        downloaded = provider.download(results[0], folder)
        converted = asyncio.run(downloader.convert.convert(downloaded))
        print(converted)


def test_song():
    sp_result = spotify.track("https://open.spotify.com/track/1BnODvOuKbTnAZYkMVzJCL")
    song = Song.from_spotify(sp_result)

    results = provider.search(song)
    downloaded = provider.download(results[0], folder)
    converted = asyncio.run(downloader.convert.convert(downloaded))
    print(converted)


if __name__ == "__main__":
    test_playlist()
