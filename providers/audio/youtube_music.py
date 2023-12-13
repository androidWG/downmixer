import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

import yt_dlp
import ytmusicapi

import matching
from file_tools import AudioCodecs
from library import Artist, Album, Song
from providers import BaseAudioProvider, ProviderSearchResult, Download, ProviderType

logger = logging.getLogger("downmixer").getChild(__name__)


def artist_from_ytmusic(data: Dict[str, Any]) -> Artist:
    return Artist(name=data["name"])


def album_from_ytmusic(data: Dict[str, Any]) -> Album:
    return Album(name=data["name"])


def song_from_ytmusic(data: Dict[str, Any]) -> Song:
    return Song(
        name=data["title"],
        artists=[artist_from_ytmusic(x) for x in data["artists"]],
        album=album_from_ytmusic(data["album"]),
        duration=data["duration_seconds"],
        url=f"https://music.youtube.com/watch?v={data['videoId']}",
    )


def search_result_from_ytmusic(original_song, result_song) -> ProviderSearchResult:
    return ProviderSearchResult(
        provider="ytmusic",
        provider_type=ProviderType.AUDIO,
        original_song=original_song,
        result_song=result_song,
        match=matching.match(original_song, result_song),
    )


class YouTubeMusicAudioProvider(BaseAudioProvider):
    provider_name = "youtube-music"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.client = ytmusicapi.YTMusic()

        options = {"encoding": "UTF-8", "format": "bestaudio"}
        self.youtube_dl = yt_dlp.YoutubeDL(options)
        logger.debug(f"Initialized YoutubeDL client with options: {options}")

    def search(self, song: Song) -> Optional[List[ProviderSearchResult]]:
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

    def download(
        self, result: ProviderSearchResult, path: str = ""
    ) -> Optional[Download]:
        logger.info(
            f"Starting download for search result '{result.result_song.title}' with URL {result.result_song.url}"
        )

        # TODO: check before replacing file
        # TODO: make file download to temp folder
        if path != "":
            # Define output path of YoutubeDL on the fly
            self.youtube_dl.params["outtmpl"]["default"] = path + "/%(id)s.%(ext)s"
        url = result.result_song.url
        metadata = self.youtube_dl.extract_info(url, download=True)
        logger.info("Finished downloading")

        downloaded = metadata["requested_downloads"][0]

        logger.debug("Creating download object")
        return Download(
            provider=self.provider_name,
            search_result=result,
            filename=Path(downloaded["filepath"]),
            bitrate=downloaded["abr"],
            audio_codec=AudioCodecs(downloaded["acodec"]),
        )
