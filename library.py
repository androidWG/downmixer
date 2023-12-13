from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Any, Dict

from slugify import slugify


class AlbumType(Enum):
    ALBUM = 1
    SINGLE = 2
    COMPILATION = 3


class BaseLibraryItem:
    @classmethod
    def from_spotify(cls, data: Dict[str, Any]):
        pass

    @classmethod
    def from_spotify_list(cls, data: List[Dict]) -> List:
        return [cls.from_spotify(x) for x in data]


@dataclass
class Artist(BaseLibraryItem):
    name: str
    images: Optional[List[str]] = None
    genres: Optional[List[Dict]] = None
    uri: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_spotify(cls, data: Dict[str, Any]) -> "Artist":
        return cls(
            name=data["name"],
            images=data["images"] if "images" in data.keys() else None,
            genres=data["genres"] if "genres" in data.keys() else None,
            uri=data["uri"],
            url=data["external_urls"]["spotify"],
        )

    def slug(self) -> "Artist":
        return Artist(
            name=slugify(self.name),
            images=self.images,
            genres=[slugify(x) for x in self.genres] if self.genres else None,
            uri=self.uri,
            url=self.url,
        )


@dataclass
class Album(BaseLibraryItem):
    name: str
    available_markets: Optional[List[str]] = None
    artists: Optional[List[Artist]] = None
    date: Optional[str] = None
    track_count: Optional[int] = None
    images: Optional[List[Dict]] = None
    uri: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_spotify(cls, data: Dict[str, Any]) -> "Album":
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
    name: str
    artists: List[Artist]
    duration: float  # in seconds
    album: Optional[Album] = None
    available_markets: Optional[List[str]] = None
    date: Optional[str] = None
    track_number: Optional[int] = None
    isrc: Optional[str] = None
    uri: Optional[str] = None
    url: Optional[str] = None
    lyrics: Optional[str] = None

    @classmethod
    def from_spotify(cls, data: Dict[str, Any]) -> "Song":
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
    def from_spotify_list(cls, data: List[Dict]) -> List:
        return [cls.from_spotify(x["track"]) for x in data]

    def slug(self) -> "Song":
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
        return self.artists[0].name + " - " + self.name

    @property
    def full_title(self) -> str:
        return (", ".join([x.name for x in self.artists])) + " - " + self.name


@dataclass
class DownloadInfo:
    song: Song
    url: str
    provider: str
    filename: Path


@dataclass
class Playlist(BaseLibraryItem):
    name: str
    description: Optional[str] = None
    tracks: Optional[List[Song]] = None
    images: Optional[List[Dict]] = None
    uri: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_spotify(cls, data: Dict[str, Any]):
        return Playlist(
            name=data["name"],
            description=data["description"],
            tracks=Song.from_spotify_list(data["tracks"]["items"]),
            images=data["images"],
            uri=data["uri"],
            url=data["url"],
        )
