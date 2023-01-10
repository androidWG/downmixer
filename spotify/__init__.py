import logging

from spotipy import SpotifyOAuth

from spotify.client import SpotipyClient
from spotify.downloader import Downloader

logger = logging.getLogger("downmixer").getChild(__name__)


class Spotify:
    def __init__(self):
        self._downloader: Downloader | None = None
        self._spotipy_client: SpotipyClient | None = None

    def login(self):
        scope = "user-library-read,playlist-read-private"
        logger.debug("Creating SpotifyClient, asking user to log in...")
        self._spotipy_client = SpotipyClient(auth_manager=SpotifyOAuth(scope=scope))
        logger.info("Creaeted spotipy client")

        self._downloader = Downloader()
