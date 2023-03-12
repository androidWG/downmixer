import logging
from pathlib import Path
from typing import Optional, Any

import yt_dlp
import ytmusicapi
from requests import session
from yt_dlp import GeoUtils

from downmixer import matching
from downmixer.file_tools import AudioCodecs
from downmixer.library import Artist, Album, Song
from downmixer.providers import BaseAudioProvider, AudioSearchResult, Download

logger = logging.getLogger("downmixer").getChild(__name__)


def artist_from_ytmusic(data: dict[str, Any]) -> Artist:
    """Create an Artist instance from a dict provided by the YouTube Music API search function. Sadly the only
    metadata of use form the search results is the title of the artist. More info on the result's schema [here](
    https://ytmusicapi.readthedocs.io/en/stable/reference.html#search).

    Args:
        data (dict):
            Dictionary provided by the YouTube Music API from the
            [`ytmusicapi`](https://github.com/sigma67/ytmusicapi) package.

    Returns:
        Artist instance populated from the dict.
    """
    return Artist(name=data["name"])


def album_from_ytmusic(data: dict[str, Any]) -> Album:
    """Create an Album instance from a dict provided by the YouTube Music API search function. Sadly the only
    metadata of use form the search results is the title of the album. More info on the result's schema [here](
    https://ytmusicapi.readthedocs.io/en/stable/reference.html#search).

    Args:
        data (dict):
            Dictionary provided by the YouTube Music API from the
            [`ytmusicapi`](https://github.com/sigma67/ytmusicapi) package.

    Returns:
        Album instance populated from the dict.
    """
    return Album(name=data["name"])


def song_from_ytmusic(data: dict[str, Any]) -> Song:
    """Create a Song instance from a dict provided by the YouTube Music API search function, including the Artist and
    Album objects. More info on the result's schema
    [here](https://ytmusicapi.readthedocs.io/en/stable/reference.html#search).

    Args:
        data (dict):
            Dictionary provided by the YouTube Music API from the
            [`ytmusicapi`](https://github.com/sigma67/ytmusicapi) package.

    Returns:
        Song instance populated from the dict..
    """
    return Song(
        name=data["title"],
        artists=[artist_from_ytmusic(x) for x in data["artists"]],
        album=album_from_ytmusic(data["album"]),
        duration=data["duration_seconds"],
        url=f"https://music.youtube.com/watch?v={data['videoId']}",
    )


def search_result_from_ytmusic(
    original_song: Song, result_song: Song
) -> AudioSearchResult:
    """Create an AudioSearchResult instance from a dict provided by the YouTube Music API search function. Sadly the only
    metadata of use form the search results is the title of the artist. More info on the result's schema [here](
    https://ytmusicapi.readthedocs.io/en/stable/reference.html#search).

    Args:
        original_song (Song): Instance of a song from Spotify that will be compared against this search result.
        result_song (Song): Song extracted from the search result info.

    Returns:
        AudioSearchResult from YT Music.
    """
    return AudioSearchResult(
        provider="ytmusic",
        _original_song=original_song,
        _result_song=result_song,
        match=matching.match(original_song, result_song),
        download_url=result_song.url,
    )


class YouTubeMusicAudioProvider(BaseAudioProvider):
    provider_name = "youtube-music"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        client_session = session()
        # if kwargs.get("geo_bypass"):
        #     client_session.headers.update(
        #         {"X-Forwarded-For": GeoUtils.random_ipv4("US")}
        #     )

        # TODO: Some testing relating to this ⬇️
        # For some reason some songs like 70tjloUDVlGYkapPPTWRxU weren't found via ISRC if the language param was not
        # specified 🤷🏻‍♀️. Selecting English bought a completely fucked up result too. I copied de (aka German)
        # from spotDL
        self.client = ytmusicapi.YTMusic(language="de", requests_session=client_session)

        options = {"encoding": "UTF-8", "format": "bestaudio"}
        self.youtube_dl = yt_dlp.YoutubeDL(options)
        logger.debug(f"Initialized YoutubeDL client with options: {options}")

    async def search(self, song: Song) -> Optional[list[AudioSearchResult]]:
        logger.info(f"Initializing search for song '{song.title}' with URI {song.uri}")
        if song.isrc:
            query = song.isrc
        else:
            query = song.title

        # TODO: redo search if ISRC isn't found
        logger.debug(f"Searching query '{query}'")
        results = self.client.search(query, filter="songs", ignore_spelling=True)

        if len(results) == 0:
            logger.info("Search returned no results")
            return None

        result_objects = []
        for r in results:
            result_song = song_from_ytmusic(r)
            search_result = search_result_from_ytmusic(song, result_song)
            result_objects.append(search_result)
            logger.debug(
                f"Found song '{result_song.title}' with URL {result_song.url}, match value {search_result.match.sum}"
            )

        ordered_results = sorted(
            result_objects, reverse=True, key=lambda x: x.match.sum
        )
        logger.info(f"Ordered {len(ordered_results)} results")
        return ordered_results

    async def download(
        self, result: AudioSearchResult, path: str = ""
    ) -> Optional[Download]:
        logger.info(
            f"Starting download for search result '{result.song.title}' with URL {result.download_url}"
        )

        # TODO: check before replacing file
        # TODO: make file download to temp folder
        if path != "":
            # Define output path of YoutubeDL on the fly
            self.youtube_dl.params["outtmpl"]["default"] = path + "/%(id)s.%(ext)s"
        url = result.download_url
        metadata = self.youtube_dl.extract_info(url, download=True)
        logger.info("Finished downloading")

        downloaded = metadata["requested_downloads"][0]

        logger.debug("Creating download object")
        return Download.from_parent(
            parent=result,
            filename=Path(downloaded["filepath"]),
            bitrate=downloaded["abr"],
            audio_codec=AudioCodecs(downloaded["acodec"]),
        )
