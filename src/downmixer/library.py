"""Data classes to hold standardized metadata about songs, artists, and albums."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any

from slugify import slugify


class AlbumType(Enum):
    ALBUM = 1
    SINGLE = 2
    COMPILATION = 3


class BaseLibraryItem:
    """Base class for library items containing standard methods to easily create class instances from the Spotify
    API."""

    @classmethod
    def from_spotify(cls, data: dict[str, Any]):
        """Create an instance of this class from a Spotify API dict.

        Args:
            data (dict[str, Any]): Dictionary with data from the Spotify API.

        Returns:
             An instance of this class.
        """
        pass

    @classmethod
    def from_spotify_list(cls, data: list[dict]) -> list:
        """Creates a list of instances of this class from a list of Spotify API dicts.

        Args:
            data (list[dict]): List with dictionaries with data from the Spotify API.

        Returns:
            A list with instances of this class.
        """
        return [cls.from_spotify(x) for x in data]


@dataclass
class Artist(BaseLibraryItem):
    """Holds info about an artist."""

    name: str
    images: Optional[list[str]] = None
    genres: Optional[list[dict]] = None
    uri: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_spotify(cls, data: dict[str, Any]) -> "Artist":
        return cls(
            name=data["name"],
            images=data["images"] if "images" in data.keys() else None,
            genres=data["genres"] if "genres" in data.keys() else None,
            uri=data["uri"],
            url=data["external_urls"]["spotify"],
        )

    def slug(self) -> "Artist":
        """Returns self with sluggified text attributes."""
        return Artist(
            name=slugify(self.name),
            images=self.images,
            genres=[slugify(x) for x in self.genres] if self.genres else None,
            uri=self.uri,
            url=self.url,
        )


@dataclass
class Album(BaseLibraryItem):
    """Holds info about an album."""

    name: str
    available_markets: Optional[list[str]] = None
    artists: Optional[list[Artist]] = None
    date: Optional[str] = None
    track_count: Optional[int] = None
    images: Optional[list[dict]] = None
    uri: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_spotify(cls, data: dict[str, Any]) -> "Album":
        return cls(
            available_markets=data["available_markets"],
            name=data["name"],
            artists=Artist.from_spotify_list(data["artists"]),
            date=data["release_date"],
            track_count=data["total_tracks"],
            images=data["images"],
            uri=data["uri"],
            url=data["external_urls"]["spotify"],
        )

    def slug(self) -> "Album":
        """Returns self with sluggified text attributes."""
        return Album(
            name=slugify(self.name),
            available_markets=self.available_markets,
            artists=[x.slug for x in self.artists] if self.artists else None,
            date=self.date,
            track_count=self.track_count,
            images=self.images,
            uri=self.uri,
            url=self.url,
        )


@dataclass
class Song(BaseLibraryItem):
    """Holds info about a song."""

    name: str
    artists: list[Artist]
    duration: float = 0  # in seconds
    album: Optional[Album] = None
    available_markets: Optional[list[str]] = None
    date: Optional[str] = None
    track_number: Optional[int] = None
    isrc: Optional[str] = None
    lyrics: Optional[str] = None
    uri: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_spotify(cls, data: dict[str, Any]) -> "Song":
        return cls(
            available_markets=data["available_markets"],
            name=data["name"],
            artists=Artist.from_spotify_list(data["artists"]),
            album=Album.from_spotify(data["album"]),
            duration=data["duration_ms"] / 1000,
            date=data["release_date"] if "release_date" in data.keys() else None,
            track_number=data["track_number"],
            isrc=data["external_ids"]["isrc"],
            uri=data["uri"],
            url=data["external_urls"]["spotify"],
        )

    @classmethod
    def from_spotify_list(cls, data: list[dict]) -> list:
        return [cls.from_spotify(x["track"]) for x in data]

    def slug(self) -> "Song":
        """Returns self with sluggified text attributes."""
        return Song(
            name=slugify(self.name),
            artists=[x.slug() for x in self.artists],
            album=self.album.slug() if self.album else None,
            available_markets=self.available_markets,
            date=self.date,
            duration=self.duration,
            track_number=self.track_number,
            isrc=self.isrc,
            uri=self.uri,
            url=self.url,
            lyrics=slugify(self.lyrics) if self.lyrics else None,
        )

    @property
    def title(self) -> str:
        """str: Title of the song, including artist, in the format '[primary artist] - [song name]'."""
        return self.artists[0].name + " - " + self.name

    @property
    def full_title(self) -> str:
        """str: Full title of the song, including all artists, in the format [artist 1, artist 2, ...] - [song name]."""
        return (", ".join(x.name for x in self.artists)) + " - " + self.name

    @property
    def all_artists(self) -> str:
        """str: All artists' names, separated by a comma."""
        return ", ".join(x.name for x in self.artists)


@dataclass
class Playlist(BaseLibraryItem):
    name: str
    description: Optional[str] = None
    tracks: Optional[list[Song]] = None
    images: Optional[list[dict]] = None
    uri: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_spotify(cls, data: dict[str, Any]):
        return Playlist(
            name=data["name"],
            description=data["description"],
            tracks=Song.from_spotify_list(data["tracks"]["items"]),
            images=data["images"],
            uri=data["uri"],
            url=data["url"],
        )
