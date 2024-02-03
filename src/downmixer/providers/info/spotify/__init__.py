import logging

import spotipy

from downmixer.library import Song, Playlist
from downmixer.providers import BaseInfoProvider
from .utils import check_valid, ResourceType

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


class SpotifyInfoProvider(BaseInfoProvider):
    def __init__(self):
        super().__init__()
        # TODO: Manage auth properly
        self.client = spotipy.Spotify(
            auth_manager=spotipy.SpotifyOAuth(
                scope="user-library-read,user-read-private"
            )
        )

        self.connected = True

    def check_valid_url(self, url: str, type_filter: list[ResourceType] = None) -> bool:
        return utils.check_valid(url, type_filter)

    def _saved_tracks(
        self, limit: int = 20, offset: int = 0, market: str | None = None
    ) -> list[Song]:
        """Helper function to get a list of Song objects instead of just a dict from the Spotify API."""
        results = self.client.current_user_saved_tracks(
            limit=limit, offset=offset, market=market
        )
        return Song.from_spotify_list(results["items"])

    def _playlists(self, limit: int = 50, offset: int = 0) -> list[Playlist]:
        """Helper function to get a list of Playlist objects instead of just a dict from the Spotify API."""
        results = self.client.current_user_playlists(limit=limit, offset=offset)
        return Playlist.from_spotify_list(results["items"])

    def _playlist_songs(self, playlist_id: Playlist | str) -> list[Song]:
        """Helper function to get a list of Song objects instead of just a dict from the Spotify API."""
        if type(playlist_id) == Playlist:
            url = playlist_id.url
        else:
            url = playlist_id

        results = self.client.playlist_items(limit=100, playlist_id=url)
        return Song.from_spotify_list(results["items"])

    def get_song(self, track_id: str) -> Song:
        super().get_song(track_id)

        result = self.client.track(track_id)
        return Song.from_spotify(result)

    def get_all_playlists(self) -> list[Playlist]:
        super().get_all_playlists()

        results = _get_all(self._playlists)
        return Playlist.from_spotify_list(results)

    def get_all_saved_tracks(self) -> list[Song]:
        super().get_all_saved_tracks()

        results = _get_all(self._saved_tracks, limit=50)
        return Song.from_spotify_list(results)

    def get_all_playlist_songs(self, playlist_id: str) -> list[Song]:
        super().get_all_playlist_songs(playlist_id)

        return self._playlist_songs(playlist_id)
