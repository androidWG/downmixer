import importlib
import pkgutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from library import Song, DownloadInfo
from matching import MatchResult


@dataclass
class ProviderSearchResult:
    provider: str
    original_song: Song
    result_song: Song
    match_result: MatchResult


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

    def download_result(self, result: ProviderSearchResult) -> Optional[DownloadInfo]:
        """Downloads a search result.

        :param result: The ProviderSearchResult that matches with this provider class.
        :return: DownloadInfo object with the downloaded file information.
        :rtype: Optional[DownloadInfo]
        """
        downloaded = self._download(result.result_song.url)
        return DownloadInfo(
            provider=self.provider_name,
            url=result.result_song.url,
            song=result.original_song,
            filename=downloaded.absolute(),
        )

    def _download(self, url: str) -> Optional[Path]:
        """Downloads the file from the URL. Can return None if a problem occurs.

        :param url: URL from this provider to download from.
        :return: Path of the downloaded file.
        :rtype: Optional[Path]
        """
        raise NotImplementedError


def get_all_providers():
    package = sys.modules[__name__]
    return [
        importlib.import_module(__name__ + "." + name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
    ]
