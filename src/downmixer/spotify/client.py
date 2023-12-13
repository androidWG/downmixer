import logging

import spotipy

from downmixer.library import Song, Playlist
from downmixer.spotify.utils import check_valid, ResourceType

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


class SpotifyClient:
    def __init__(self, scope: str):
        self.client = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(scope=scope))

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

    def _playlist_songs(self, playlist: Playlist | str) -> list[Song]:
        """Helper function to get a list of Song objects instead of just a dict from the Spotify API."""
        if type(playlist) == Playlist:
            url = playlist.url
        else:
            url = playlist

        results = self.client.playlist_items(limit=100, playlist_id=url)
        return Song.from_spotify_list(results["items"])

    def song(self, track_id: str) -> Song:
        """Retireve a song (a.k.a. a "track") from the Spotify API. Returns a new Song object with the metadata from
        Spotify.

        Args:
            track_id (str): A string containing a valid Spotify ID, URI or URL. Check the
                [Spotify API docs](https://developer.spotify.com/documentation/web-api/#spotify-uris-and-ids)
                for more info.

        Returns:
            Song object with the metadata retireved from Spotify.
        """
        if not check_valid(track_id, [ResourceType.TRACK]):
            raise ValueError(
                f"{track_id} is an invalid Spotify track ID. Make sure it mactches either an URI, URL or ID. "
                f"More information: https://developer.spotify.com/documentation/web-api/#spotify-uris-and-ids"
            )

        url = track_id

        result = self.client.track(url)
        return Song.from_spotify(result)

    def all_playlists(self) -> list[Playlist]:
        """Retrives the all the user's playlists in a list. Requires the [`playlist-read-private` scope](
        https://developer.spotify.com/documentation/general/guides/authorization/scopes/#playlist-read-private) to
        read private playlists and the [`playlist-read-collaborative` scope](
        https://developer.spotify.com/documentation/general/guides/authorization/scopes/#playlist-read-collaborative) to
        read collaborative playlists.

        Returns:
            User's playlists as a list of Playlist objects.
        """
        results = _get_all(self._playlists)
        return Playlist.from_spotify_list(results)

    def all_saved_tracks(self) -> list[Song]:
        """Retrives the all the user's saved tracks in a list. Requires the [`user-library-read` scope]
        (https://developer.spotify.com/documentation/general/guides/authorization/scopes/#user-library-read).

        Returns:
            User's playlists as a list of Playlist objects.
        """
        results = _get_all(self._saved_tracks, limit=50)
        return Song.from_spotify_list(results)

    def all_playlist_songs(self, playlist_id: str) -> list[Song]:
        """Retrives the all the songs from a playlist in a list. Requires the [`playlist-read-private` scope](
        https://developer.spotify.com/documentation/general/guides/authorization/scopes/#playlist-read-private) to
        read private playlists and the [`playlist-read-collaborative` scope](
        https://developer.spotify.com/documentation/general/guides/authorization/scopes/#playlist-read-collaborative) to
        read collaborative playlists.

        Args:
            playlist_id (str): A string containing a valid Spotify ID, URI or URL. Check the
                [Spotify API docs](https://developer.spotify.com/documentation/web-api/#spotify-uris-and-ids)
                for more info.

        Returns:
            User's playlists as a list of Playlist objects.
        """
        if not check_valid(playlist_id, [ResourceType.PLAYLIST]):
            raise ValueError(
                f"{playlist_id} is an invalid Spotify track ID. Make sure it mactches either an URI, URL or ID. "
                f"More information: https://developer.spotify.com/documentation/web-api/#spotify-uris-and-ids"
            )

        results = _get_all(self._playlist_songs, limit=100, playlist_id=playlist_id)
        return Song.from_spotify_list(results)
