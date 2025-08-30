from typing import Any

from downmixer.library import Album, Artist, Song, Playlist


class SpotifyArtist(Artist):
    @classmethod
    def from_provider(
        cls, data: dict[str, Any], extra_data: dict[str, Any] = None
    ) -> "SpotifyArtist":
        return cls(
            name=data["name"],
            images=data["images"] if "images" in data.keys() else None,
            # TODO: Test the data structure of genres from Spotify
            genres=data["genres"] if "genres" in data.keys() else None,
            id=data["uri"],
            url=data["external_urls"]["spotify"],
        )


class SpotifyAlbum(Album):
    @classmethod
    def from_provider(
        cls, data: dict[str, Any], extra_data: dict[str, Any] = None
    ) -> "SpotifyAlbum":
        return cls(
            available_markets=data["available_markets"],
            name=data["name"],
            artists=SpotifyArtist.from_provider_list(data["artists"]),
            date=data["release_date"],
            track_count=data["total_tracks"],
            cover=(data["images"][0]["url"] if len(data["images"]) > 0 else None),
            id=data["uri"],
            url=data["external_urls"]["spotify"],
        )

    @classmethod
    def from_provider_list(
        cls, data: list[Any], extra_data: dict = None
    ) -> list["SpotifyAlbum"]:
        """Takes in a list of albums from the Spotify API and returns a list of SpotifyAlbums."""
        return [cls.from_provider(x["album"], extra_data) for x in data]


class SpotifySong(Song):
    @classmethod
    def from_provider(
        cls, data: dict[str, Any], extra_data: dict[str, Any] = None
    ) -> "SpotifySong":
        if "album" in data.keys():
            album = data["album"]
        elif "album" in extra_data.keys():
            album = extra_data["album"]
        else:
            album = None

        return cls(
            available_markets=data["available_markets"],
            name=data["name"],
            artists=SpotifyArtist.from_provider_list(data["artists"]),
            album=(SpotifyAlbum.from_provider(album) if album else None),
            duration=data["duration_ms"] / 1000,
            date=data["release_date"] if "release_date" in data.keys() else None,
            track_number=data["track_number"],
            isrc=(
                data["external_ids"]["isrc"] if "external_ids" in data.keys() else None
            ),
            id=data["uri"],
            url=data["external_urls"]["spotify"],
            cover=(
                album["images"][0]["url"]
                if album and len(album["images"]) > 0
                else None
            ),
        )

    @classmethod
    def from_provider_list(
        cls, data: list[dict], extra_data: dict[str, Any] = None
    ) -> list["SpotifySong"]:
        """Takes in a list of tracks from the Spotify API and returns a list of SpotifySongs."""
        try:
            return [cls.from_provider(x["track"], extra_data) for x in data]
        except KeyError:
            return [cls.from_provider(x, extra_data) for x in data]


class SpotifyPlaylist(Playlist):
    @classmethod
    def from_provider(
        cls, data: dict[str, Any], extra_data: dict[str, Any] = None
    ) -> "SpotifyPlaylist":
        return cls(
            name=data["name"],
            description=data["description"],
            tracks=SpotifySong.from_provider_list(data["tracks"]["items"]),
            images=data["images"],
            id=data["uri"],
            url=data["url"],
        )
