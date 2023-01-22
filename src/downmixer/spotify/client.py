import logging
from typing import List

import spotipy

from src.downmixer.library import Song, Playlist

logger = logging.getLogger("downmixer").getChild(__name__)


def _get_all(func, limit=50, *args, **kwargs):
    counter = 0
    next_url = ""
    items = []

    while next_url is not None:
        results = func(*args, **kwargs, limit=limit, offset=limit * counter)
        next_url = results["next"]
        counter += 1
        items += results["items"]

    return items


class SpotipyClient:
    def __init__(self, scope: str):
        self.client = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(scope=scope))

    def _saved_tracks(self, limit=20, offset=0, market=None) -> List[Song]:
        results = self.client.current_user_saved_tracks(
            limit=limit, offset=offset, market=market
        )
        return Song.from_spotify_list(results["items"])

    def _playlists(self, limit=50, offset=0) -> List[Playlist]:
        results = self.client.current_user_playlists(limit=limit, offset=offset)
        return Playlist.from_spotify_list(results["items"])

    def _playlist_songs(self, playlist: Playlist | str) -> List[Song]:
        if type(playlist) == Playlist:
            url = playlist.url
        else:
            url = playlist

        results = self.client.playlist_items(limit=100, playlist_id=url)
        return Song.from_spotify_list(results["items"])

    def song(self, song: Song | str) -> Song:
        if type(song) == Playlist:
            url = song.url
        else:
            url = song

        result = self.client.track(url)
        return Song.from_spotify(result)

    def all_playlists(self):
        results = _get_all(self._playlists)
        return Playlist.from_spotify_list(results)

    def all_saved_tracks(self):
        results = _get_all(self._saved_tracks, limit=50)
        return Song.from_spotify_list(results)

    def all_playlist_songs(self, playlist):
        results = _get_all(self._playlist_songs, limit=100, playlist_id=playlist)
        return Song.from_spotify_list(results)
