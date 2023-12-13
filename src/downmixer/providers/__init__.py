import importlib
import pkgutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from src.downmixer.file_tools import AudioCodecs
from src.downmixer.library import Song
from src.downmixer.matching import MatchResult, MatchQuality


@dataclass
class ProviderSearchResult:
    provider: str
    match: MatchResult
    download_url: str
    _original_song: Song
    _result_song: Song

    @property
    def song(self) -> Song:
        if self.match.quality == MatchQuality.PERFECT:
            return self._original_song
        else:
            return self._result_song


@dataclass
class LyricsSearchResult:
    provider: str
    match: MatchResult
    name: str
    artist: str
    url: str


@dataclass
class Download(ProviderSearchResult):
    filename: Path
    bitrate: float
    audio_codec: AudioCodecs

    @classmethod
    def from_parent(cls, parent: ProviderSearchResult, filename: Path, bitrate: float, audio_codec: AudioCodecs):
        return cls(
            provider=parent.provider,
            match=parent.match,
            _result_song=parent._result_song,
            _original_song=parent._original_song,
            download_url=parent.download_url,
            filename=filename,
            bitrate=bitrate,
            audio_codec=audio_codec
        )


class BaseAudioProvider:
    """
    Base class for all audio providers. Defines the interface that any audio provider in Downmixer should use.
    """
    provider_name = ""

    def search(self, song: Song) -> Optional[List[ProviderSearchResult]]:
        """Returns a list of ProviderSearchResult objects ordered by match result, highest to lowest. Can return None if a problem occurs.

        :param song: Song object which will be searched.
        """
        raise NotImplementedError

    def download(self, result: ProviderSearchResult, path: Path) -> Optional[Download]:
        """Downloads a search result.

        :param result: The ProviderSearchResult that matches with this provider class.
        :param path: The folder in which the file will be downloaded.
        :return: DownloadInfo object with the downloaded file information.
        :rtype: Optional[Download]
        """
        raise NotImplementedError


class BaseLyricsProvider:
    """
    Base class for all lyrics providers. Defines the interface that any lyrics provider in Downmixer should use.
    """
    provider_name = ""

    def search(self, song: Song) -> Optional[List[ProviderSearchResult]]:
        """Returns a list of ProviderSearchResult objects ordered by match result, highest to lowest. Can return None if a problem occurs.

        :param song: Song object which will be searched.
        """
        raise NotImplementedError

    def get_lyrics(self, result: ProviderSearchResult) -> Optional[str]:
        """Downloads a search result.

        :param result: The ProviderSearchResult that matches with this provider class.
        :return: String object containing the found lyrics, or None if a problem occured.
        :rtype: Optional[str]
        """
        raise NotImplementedError


def get_all_audio_providers():
    package = sys.modules[__name__]
    return [
        importlib.import_module(__name__ + "." + name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
    ]
