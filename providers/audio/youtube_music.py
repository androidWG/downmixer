import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

import ytmusicapi as ytmusicapi

import matching
from library import Artist, Album, Song
from providers import BaseAudioProvider, ProviderSearchResult

logger = logging.getLogger("peppermint").getChild(__name__)


def artist_from_ytmusic(data: Dict[str, Any]) -> Artist:
    return Artist(
        name=data["name"]
    )


def album_from_ytmusic(data: Dict[str, Any]) -> Album:
    return Album(
        name=data["name"]
    )


def song_from_ytmusic(data: Dict[str, Any]) -> Song:
    return Song(
        name=data["title"],
        artists=[artist_from_ytmusic(x) for x in data["artists"]],
        album=album_from_ytmusic(data["album"]),
        duration=data["duration_seconds"]
    )


def search_result_from_ytmusic(original_song, result_song) -> ProviderSearchResult:
    return ProviderSearchResult(
        provider="ytmusic",
        original_song=original_song,
        result_song=result_song,
        match_result=matching.match(original_song, result_song)
    )


class YouTubeMusicAudioProvider(BaseAudioProvider):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.client = ytmusicapi.YTMusic()

    def download(self, url: str, song: Song) -> Optional[Path]:
        pass

    def search(self, song: Song) -> Optional[List]:
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

        ordered_results = sorted(result_objects, reverse=True, key=lambda x: x.match_result.sum)
        return ordered_results

