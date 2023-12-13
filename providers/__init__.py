import importlib
import pkgutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from library import Song
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

    def search(self, song: Song) -> Optional[List[Song]]:
        """Returns a list ordered by match result, highest to lowest. Can return None if a problem occurs.

        :param song: Song object which will be searched.
        """
        raise NotImplementedError

    def download(self, url: str, song: Song) -> Optional[Path]:
        """Downloads the Song specified to the hardisk in . Can return None if a problem occurs.

        :param url: URL from this provider to download from.
        :param song: Song object which will be used to name the file.
        :return:
        :rtype: Optional[Path]
        """
        raise NotImplementedError


def get_all_providers():
    package = sys.modules[__name__]
    return [
        importlib.import_module(__name__ + "." + name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
    ]
