from __future__ import annotations

import logging
import re

import spotipy

from downmixer import utils
from downmixer.library import Playlist
from downmixer.providers import BaseInfoProvider, ResourceType
from .library import SpotifySong, SpotifyPlaylist, SpotifyAlbum

logger = logging.getLogger("downmixer").getChild(__name__)

resource_type_map = {
    ResourceType.SONG: "track",
    ResourceType.ALBUM: "album",
    ResourceType.PLAYLIST: "playlist",
    ResourceType.ARTIST: "artist",
}


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
    def __init__(self, options: dict = None):
        default_options = {
            "auth": {
                "scope": "user-library-read,user-follow-read,playlist-read-private",
            }
        }
        options = utils.merge_dicts_with_priority(default_options, options)
        super().__init__(options)

        # TODO: Manage auth properly
        self.client = spotipy.Spotify(
            auth_manager=spotipy.SpotifyOAuth(**options["auth"])
        )

        self.connected = True

    def get_resource_type(self, value: str) -> ResourceType | None:
        if not self.check_valid_url(value):
            return None

        pattern = r"spotify(?:.com)?(?::|\/)(\w*)(?::|\/)(?:\w{20,24})"
        matches = re.search(pattern, value)

        if matches is None:
            return None
        else:
            return list(resource_type_map.keys())[
                list(resource_type_map.values()).index(matches.group(1).lower())
            ]

    def check_valid_url(self, url: str, type_filter: list[ResourceType] = None) -> bool:
        if type_filter is None:
            type_filter = [e for e in ResourceType]

        for t in type_filter:
            regex = r"spotify.*" + resource_type_map[t] + r"(?::|\/)(\w{20,24})"
            if re.search(regex, url) is not None:
                return True

        return False

    def get_song(self, track_id: str) -> SpotifySong:
        super().get_song(track_id)

        result = self.client.track(track_id)
        return SpotifySong.from_provider(result)

    def get_all_playlist_songs(self, playlist_id: str) -> list[SpotifySong]:
        super().get_all_playlist_songs(playlist_id)

        if self.check_valid_url(playlist_id, [ResourceType.PLAYLIST]):
            results = _get_all(
                self.client.playlist_items, limit=50, playlist_id=playlist_id
            )
            return SpotifySong.from_provider_list(results)
        else:
            album_info = self.client.album(playlist_id)
            results = _get_all(self.client.album_tracks, limit=50, album_id=playlist_id)
            return SpotifySong.from_provider_list(
                results, extra_data={"album": album_info}
            )

    def get_all_user_playlists(self) -> list[SpotifyPlaylist]:
        super().get_all_user_playlists()

        results = _get_all(self.client.current_user_playlists)
        return SpotifyPlaylist.from_provider_list(results)

    def get_all_user_albums(self) -> list[Playlist]:
        super().get_all_user_albums()

        results = _get_all(self.client.current_user_saved_albums, limit=50)
        return SpotifyAlbum.from_provider_list(results)

    def get_all_user_songs(self) -> list[SpotifySong]:
        super().get_all_user_songs()

        results = _get_all(self.client.current_user_saved_tracks, limit=50)
        return SpotifySong.from_provider_list(results)
