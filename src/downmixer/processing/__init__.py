"""Takes a playlist or song and processes it using audio and lyric providers."""

import asyncio
import logging
import shutil
from pathlib import Path

from downmixer.file_tools import tag, utils
from downmixer.file_tools.convert import Converter
from downmixer.providers import (
    Download,
    get_all_info_providers,
    BaseInfoProvider,
    BaseAudioProvider,
    BaseLyricsProvider,
)
from downmixer.providers.audio.youtube_music import YouTubeMusicAudioProvider
from downmixer.providers.lyrics.azlyrics import AZLyricsProvider

logger = logging.getLogger("downmixer").getChild(__name__)


async def _convert_download(download: Download) -> Download:
    converter = Converter(download)
    return await converter.convert()


class BasicProcessor:
    def __init__(
        self,
        info_provider: BaseInfoProvider,
        audio_provider: BaseAudioProvider,
        lyrics_provider: BaseLyricsProvider,
        output_folder: Path,
        temp_folder: Path,
        threads: int = 12,
    ):
        """Basic processing class to search a specific Spotify song and download it, using the default YT Music and
        AZLyrics providers.

        Args:
            output_folder (str): Folder path where the final file will be placed.
            temp_folder (str): Folder path where temporary files will be placed and removed from when processing
                is finished.
            threads (int): Amount of threads that will simultaneously process songs.
        """
        self.output_folder: Path = Path(output_folder).absolute()
        self.temp_folder = temp_folder

        self.info_provider = info_provider
        self.audio_provider = audio_provider
        self.lyrics_provider = lyrics_provider

        self.semaphore = asyncio.Semaphore(threads)

    async def _get_lyrics(self, download: Download):
        lyrics_results = await self.lyrics_provider.search(download.song)
        if lyrics_results is not None:
            lyrics = await self.lyrics_provider.get_lyrics(lyrics_results[0])
            download.song.lyrics = lyrics

    async def pool_processing(self, song: str):
        logger.debug(f"Starting pool processing of {song}")
        async with self.semaphore:
            logger.debug(f"Processing song '{song}'")
            await self.process_song(song)

    async def process_playlist(self, playlist_id: str):
        """Makes a queue of tasks to download all songs in a Spotify playlist.

        Args:
            playlist_id (str): V"""
        songs = self.info_provider.get_all_playlist_songs(playlist_id)

        tasks = [self.pool_processing(s.uri) for s in songs]
        await asyncio.gather(*tasks)

    async def process_song(self, song_id: str):
        """Searches and downloads a song based on Spotify data.

        Args:
            song_id (str): Valid ID, URI or URL of a Spotify track.
        """
        song = self.info_provider.get_song(song_id)

        result = await self.audio_provider.search(song)
        if result is None:
            logger.warning("Song not found", extra={"songinfo": song.__dict__})
            return
        downloaded = await self.audio_provider.download(result[0], self.temp_folder)
        converted = await _convert_download(downloaded)

        await self._get_lyrics(converted)
        tag.tag_download(converted)

        new_name = (
            utils.make_sane_filename(converted.song.title) + converted.filename.suffix
        )

        self.output_folder.mkdir(parents=True, exist_ok=True)
        logger.debug(
            f"Moving file from '{converted.filename}' to '{self.output_folder}'"
        )
        shutil.move(converted.filename, self.output_folder.joinpath(new_name))
