from spotipy import SpotifyOAuth

from providers.audio.youtube_music import YouTubeMusicAudioProvider
from spotify import SpotipyClient


def test():
    scope = "user-library-read,playlist-read-private"
    spotify = SpotipyClient(auth_manager=SpotifyOAuth(scope=scope))
    saved_tracks = spotify.current_user_saved_tracks_processed()

    provider = YouTubeMusicAudioProvider()
    for t in saved_tracks:
        results = provider.search(t)
        downloaded = provider.download(results[0])
        print(downloaded)


if __name__ == "__main__":
    test()
