"""Defines base provider classes and give default lyrics and audio providers."""

import importlib
import pkgutil
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Optional, List, Type

from downmixer.file_tools import AudioCodecs
from downmixer.library import Song, Playlist
from downmixer.matching import MatchResult, MatchQuality


@dataclass
class AudioSearchResult:
    """Holds data about a result from a `BaseAudioProvider` instance."""

    provider: str
    match: MatchResult
    download_url: str
    _original_song: Song
    _result_song: Song

    @property
    def song(self) -> Song:
        """Compares the match quality with a set threshold and returns the most appropriate choice between the
        original song from Spotify or the result given by the provider.

        Returns:
            song (Song): The appropriate song object.
        """
        if self.match.quality == MatchQuality.PERFECT:
            return self._original_song
        else:
            return self._result_song


@dataclass
class LyricsSearchResult:
    """Holds data about a result from a `BaseLyricsProvider` instance."""

    provider: str
    match: MatchResult
    name: str
    artist: str
    url: str


@dataclass
class Download(AudioSearchResult):
    """A child of `AudioSearchResult` which has been successfully downloaded. Contains data about the downloaded
    file and its path.

    Attributes:
        filename (Path): Path to the downloaded song on the system.
        bitrate (float): The file's bitrate in kbps.
        audio_codec (AudioCodecs): One of the supported audio codecs from `AudioCodecs` enum.
    """

    filename: Path
    bitrate: float
    audio_codec: AudioCodecs

    @classmethod
    def from_parent(
        cls,
        parent: AudioSearchResult,
        filename: Path,
        bitrate: float,
        audio_codec: AudioCodecs,
    ):
        """Make a Download instance with the information from a parent `ProviderSearchResult` class.

        Args:
            parent (AudioSearchResult): The class instance being used.
            filename (Path): Path to the downloaded song on the system.
            bitrate (float): The file's bitrate in kbps.
            audio_codec (AudioCodecs): One of the supported audio codecs from `AudioCodecs` enum.

        Returns:
            cls (Download): Download instance with attributes from the `parent` object and other provided info.
        """
        return cls(
            provider=parent.provider,
            match=parent.match,
            _result_song=parent._result_song,
            _original_song=parent._original_song,
            download_url=parent.download_url,
            filename=filename,
            bitrate=bitrate,
            audio_codec=audio_codec,
        )


class BaseAudioProvider:
    """
    Base class for all audio providers. Defines the interface that any audio provider in Downmixer should use.
    """

    provider_name = ""

    async def search(self, song: Song) -> Optional[list[AudioSearchResult]]:
        """Retrieves search results as list of `AudioSearchResult` objects ordered by match, highest to lowest.
        Can return None if a problem occurs.

        Args:
            song (Song): Song object which will be searched.

        Returns:
            Optional list containing the search results as `AudioSearchResult` objects.
        """
        raise NotImplementedError

    async def download(
        self, result: AudioSearchResult, path: Path
    ) -> Optional[Download]:
        """Downloads, using this provider, a search result to the path specified.

        Args:
            result (AudioSearchResult): The `AudioSearchResult` that matches with this provider class.
            path (Path): The folder (not filename) in which the file will be downloaded.

        Returns:
            Download object with the downloaded file information.
        """
        raise NotImplementedError


class BaseLyricsProvider:
    """
    Base class for all lyrics providers. Defines the interface that any lyrics provider in Downmixer should use.
    """

    provider_name = ""

    async def search(self, song: Song) -> Optional[list[LyricsSearchResult]]:
        """Retrieves search results as list of `LyricsSearchResult` objects ordered by match, highest to lowest.
        Can return None if a problem occurs.

        Args:
            song (Song): Song object which will be searched.

        Returns:
            Optional list containing the search results as `LyricsSearchResult` objects.
        """
        raise NotImplementedError

    async def get_lyrics(self, result: LyricsSearchResult) -> Optional[str]:
        """Retrieves lyrics for a specific search result from this provider.

        Args:
            result (LyricsSearchResult): The song being searched.

        Returns:
            Optional string with the lyrics of the song.
        """
        raise NotImplementedError


class BaseInfoProvider:
    """Base class for all song info providers. Defines the interface that any song info provider in Downmixer should
    use."""

    def get_song(self, track_id: str) -> Song:
        pass

    def get_all_playlist_songs(self, playlist_id: str) -> list[Song]:
        pass

    def get_all_playlists(self) -> list[Playlist]:
        pass

    def get_all_saved_tracks(self) -> list[Song]:
        pass


# TODO: Add support for importing third-party providers
def _import_submodules(prefix: str):
    providers_path = Path(__file__).parent.joinpath(prefix)
    current_package_name = sys.modules[__name__].__name__

    for loader, name, is_pkg in pkgutil.walk_packages([providers_path]):
        importlib.import_module(f"{current_package_name}.{prefix}.{name}")


def get_all_audio_providers() -> list[Type[BaseAudioProvider]]:
    _import_submodules("audio")
    return BaseAudioProvider.__subclasses__()


def get_all_lyrics_providers() -> list[Type[BaseLyricsProvider]]:
    _import_submodules("lyrics")
    return BaseLyricsProvider.__subclasses__()


def get_all_info_providers() -> list[Type[BaseInfoProvider]]:
    _import_submodules("info")
    return BaseInfoProvider.__subclasses__()
