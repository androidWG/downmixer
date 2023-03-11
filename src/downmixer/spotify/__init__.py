import logging

from spotipy import SpotifyOAuth

from downmixer.spotify.client import SpotipyClient

logger = logging.getLogger("downmixer").getChild(__name__)


class Spotify:
    def __init__(self):
        self._spotipy_client: SpotipyClient | None = None

    def login(self):
        scope = "user-library-read,playlist-read-private"
        logger.debug("Creating SpotifyClient, asking user to log in...")
        self._spotipy_client = SpotipyClient(auth_manager=SpotifyOAuth(scope=scope))
        logger.info("Creaeted spotipy client")
