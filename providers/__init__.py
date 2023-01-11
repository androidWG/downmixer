import importlib
import pkgutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from downloader import AudioCodecs
from library import Song
from matching import MatchResult


@dataclass
class ProviderSearchResult:
    provider: str
    original_song: Song
    result_song: Song
    match: MatchResult


@dataclass
class Download:
    provider: str
    search_result: ProviderSearchResult
    filename: Path
    bitrate: float
    audio_codec: AudioCodecs


class BaseAudioProvider:
    """
    Base class for all other providers. Provides some common functionality.
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


def get_all_providers():
    package = sys.modules[__name__]
    return [
        importlib.import_module(__name__ + "." + name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
    ]
