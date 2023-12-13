import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

import yt_dlp
import ytmusicapi

import matching
from downloader import AudioCodecs
from library import Artist, Album, Song
from providers import BaseAudioProvider, ProviderSearchResult, Download

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
        original_song=original_song,
        result_song=result_song,
        match_result=matching.match(original_song, result_song),
    )


class YouTubeMusicAudioProvider(BaseAudioProvider):
    provider_name = "youtube-music"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.client = ytmusicapi.YTMusic()
        self.youtube_dl = yt_dlp.YoutubeDL({"encoding": "UTF-8", "format": "bestaudio"})

    def search(self, song: Song) -> Optional[List[ProviderSearchResult]]:
        if song.isrc:
            query = song.isrc
        else:
            query = song.title

        results = self.client.search(query, filter="songs", ignore_spelling=True)

        if len(results) == 0:
            return None

        result_objects = []
        for r in results:
            result_song = song_from_ytmusic(r)
            result_objects.append(search_result_from_ytmusic(song, result_song))

        ordered_results = sorted(
            result_objects, reverse=True, key=lambda x: x.match_result.sum
        )
        return ordered_results

    def download(self, result: ProviderSearchResult) -> Optional[Download]:
        url = result.result_song.url
        metadata = self.youtube_dl.extract_info(url, download=True)
        downloaded = metadata["requested_downloads"][0]
        return Download(
            provider=self.provider_name,
            search_result=result,
            filename=Path(downloaded["filepath"]),
            bitrate=downloaded["abr"],
            audio_codec=AudioCodecs(downloaded["acodec"]),
        )
