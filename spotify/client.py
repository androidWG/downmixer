import logging

import spotipy

from library import Song, Playlist

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


class SpotipyClient(spotipy.Spotify):
    def current_user_saved_tracks_processed(self, limit=20, offset=0, market=None):
        results = super().current_user_saved_tracks(
            limit=limit, offset=offset, market=market
        )
        return Song.from_spotify_list(results["items"])

    def current_user_playlists_processed(self, limit=50, offset=0):
        results = super().current_user_playlists(limit=limit, offset=offset)
        return Playlist.from_spotify_list(results["items"])

    def playlist_items_processed(self, playlist):
        results = super().playlist_items(limit=100, playlist_id=playlist)
        return Song.from_spotify_list(results["items"])

    def current_user_all_playlists(self):
        results = _get_all(self.current_user_playlists)
        return Playlist.from_spotify_list(results)

    def current_user_all_saved_tracks(self):
        results = _get_all(self.current_user_saved_tracks, limit=50)
        return Song.from_spotify_list(results)

    def all_playlist_items(self, playlist):
        results = _get_all(self.playlist_items, limit=100, playlist_id=playlist)
        return Song.from_spotify_list(results)
