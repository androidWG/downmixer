import logging
import os

import spotdl
from spotipy import SpotifyOAuth

from settings import Settings
from spotify.client import SpotipyClient
from spotify.downloader import Downloader

logger = logging.getLogger("peppermint").getChild(__name__)


class Spotify:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._downloader: spotdl.download.Downloader | None = None
        self._spotipy_client: SpotipyClient | None = None
        self._spotdl_client: spotdl.SpotifyClient | None = None

    def login(self):
        scope = "user-library-read,playlist-read-private"
        logger.debug("Creating SpotifyClient, asking user to log in...")
        self._spotipy_client = SpotipyClient(auth_manager=SpotifyOAuth(scope=scope))
        logger.info("Creaeted spotipy client")

        self._spotdl_client = spotdl.SpotifyClient.init(
            os.getenv("SPOTIPY_CLIENT_ID"),
            os.getenv("SPOTIPY_CLIENT_SECRET"),
            cache_path=os.path.abspath(".cache"),
        )
        logger.info("Created spotdl SpoticyClient")
        self._downloader = Downloader(
            threads=self._settings.get("threads"),
            bitrate=self._settings.get("bitrate"),
            output_format=self._settings.get("format"),
        )
