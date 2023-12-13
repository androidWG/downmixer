import asyncio
import concurrent.futures
import datetime
import logging
import sys
from enum import Enum
from pathlib import Path
from queue import Queue
from typing import Tuple, Optional, List

from settings import Settings
from spotdl import Song
from spotdl.download.downloader import DownloaderError
from spotdl.providers.audio.base import AudioProvider
from spotdl.utils.config import get_errors_path, get_temp_path
from spotdl.utils.ffmpeg import FFmpegError, convert, get_ffmpeg_path
from spotdl.utils.formatter import create_file_name
from spotdl.utils.metadata import MetadataError, embed_metadata
from spotdl.utils.search import reinit_song

logger = logging.getLogger("peppermint").getChild(__name__)


class OverwriteType(Enum):
    SKIP = 1
    OVERWITE = 2
    METADATA = 3


class Downloader:
    thread_executor = None
    semaphore = None
    loop = None
    queue = Queue()

    def __init__(
        self,
        settings: Settings,
        bitrate: Optional[str] = None,
        overwrite: OverwriteType = OverwriteType.SKIP,
        cookie_file: Optional[str] = None,
        filter_results: bool = True,
        preserve_original_audio: bool = False,
    ):
        self.settings = settings
        self.setup_loop(self.settings.get("threads"))

        ffmpeg_exec = get_ffmpeg_path()
        if ffmpeg_exec is None:
            raise DownloaderError("ffmpeg is not installed")

        ffmpeg = str(ffmpeg_exec.absolute())

        self.output_format = self.settings.get("format")
        self.threads = self.settings.get("threads")
        self.cookie_file = cookie_file
        self.overwrite = overwrite
        self.filter_results = filter_results
        self.ffmpeg = ffmpeg
        self.bitrate = bitrate
        self.preserve_original_audio = preserve_original_audio

        logger.debug("Downloader initialized")

    def setup_loop(self, threads_num):
        self.loop = (
            asyncio.new_event_loop()
            if sys.platform != "win32"
            else asyncio.ProactorEventLoop()  # type: ignore
        )
        asyncio.set_event_loop(self.loop)
        self.semaphore = asyncio.Semaphore(threads_num)
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=threads_num
        )

    async def pool_download(self, song: Song) -> Tuple[Song, Optional[Path]]:
        # tasks that cannot acquire semaphore will wait here until it's free
        # only certain amount of tasks can acquire the semaphore at the same time
        async with self.semaphore:
            return await self.loop.run_in_executor(
                self.thread_executor, self.search_and_download, song
            )

    def search(self, song: Song) -> Tuple[str, AudioProvider]:
        audio_providers: List[AudioProvider] = [
            apc(
                output_format=self.output_format,
                cookie_file=self.cookie_file,
                search_query=None,
                filter_results=self.filter_results,
            )
            for apc in self.audio_providers_classes
        ]

        for audio_provider in audio_providers:
            url = audio_provider.search(song)
            if url:
                return url, audio_provider

            logger.debug(f"{audio_provider.name} failed to find {song.display_name}")

        raise LookupError(f"No results found for song: {song.display_name}")

    def search_lyrics(self, song: Song) -> Optional[str]:
        """
        Search for lyrics using all available providers.

        ### Arguments
        - song: The song to search for.

        ### Returns
        - lyrics if successful else None.
        """

        for lyrics_provider in self.lyrics_providers:
            lyrics = lyrics_provider.get_lyrics(song.name, song.artists)
            if lyrics:
                logger.debug(
                    f"Found lyrics for {song.display_name} on {lyrics_provider.name}"
                )
                return lyrics

            logger.debug(
                f"{lyrics_provider.name} failed to find lyrics "
                f"for {song.display_name}"
            )

        return None

    def download(self, song: Song, path: Path) -> Tuple[Song, Optional[Path]]:
        # Check if we have all the metadata
        # and that the song object is not a placeholder
        # If it's None extract the current metadata
        # And reinitialize the song object
        if song.name is None and song.url:
            song = reinit_song(song, False)

        # Find song lyrics and add them to the song object
        self.add_lyrics(song)

        # Create the output file path
        output_file = create_file_name(song, str(path), self.output_format)
        temp_folder = get_temp_path()

        path.mkdir(parents=True, exist_ok=True)

        # Handle force overwriting, skipping and overwriting metadata
        if output_file.exists():
            match self.overwrite:
                case "skip":
                    logger.info(f"Skipping {song.display_name}")
                    return song, None
                case "metadata":
                    embed_metadata(
                        output_file=output_file,
                        song=song,
                        file_format=self.output_format,
                    )

                    logger.info(f"Updated metadata for {song.display_name}")

                    return song, output_file
                case "force":
                    logger.debug(f"Overwriting {song.display_name}")

        try:
            # If the song object already has a download url
            # we can skip the search, and just reinitialize the base
            # audio provider to download the song
            if song.download_url is None:
                download_url, audio_provider = self.search(song)
            else:
                download_url = song.download_url
                audio_provider = AudioProvider(
                    output_format=self.output_format,
                    cookie_file=self.cookie_file,
                    search_query=None,
                    filter_results=self.filter_results,
                )
            logger.debug(
                f"Downloading {song.display_name} using {download_url}, "
                f"audio provider: {audio_provider.name}"
            )

            # Download the song
            download_info = audio_provider.get_download_metadata(
                download_url, download=True
            )

            temp_file = Path(
                temp_folder / f"{download_info['id']}.{download_info['ext']}"
            )

            if download_info is None:
                logger.debug(
                    f"No download info found for {song.display_name}, url: {download_url}"
                )

                raise LookupError(
                    f"yt-dlp failed to get metadata for: {song.name} - {song.artist}"
                )

            self.convert_with_ffmpeg(download_info, output_file, song, temp_file)

            # Remove the temp file
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except (PermissionError, OSError) as exc:
                    raise DownloaderError(
                        f"Could not remove temp file: {temp_file}, possible duplicate song"
                    ) from exc

            download_info["filepath"] = str(output_file)

            # Set the song's download url
            if song.download_url is None:
                song.download_url = download_url

            try:
                embed_metadata(output_file, song, self.output_format)
            except Exception as exception:
                raise MetadataError(
                    "Failed to embed metadata to the song"
                ) from exception

            logger.info(f'Downloaded "{song.display_name}": {song.download_url}')

            return song, output_file
        except (Exception, UnicodeEncodeError) as exception:
            if isinstance(exception, UnicodeEncodeError):
                exception_cause = exception
                exception = DownloaderError(
                    "You may need to add PYTHONIOENCODING=utf-8 to your environment"
                )

                exception.__cause__ = exception_cause

            return song, None

    def add_lyrics(self, song):
        lyrics = self.search_lyrics(song)
        if lyrics is None:
            logger.debug(
                f"No lyrics found for {song.display_name}, "
                "lyrics providers: "
                f"{', '.join([lprovider.name for lprovider in self.lyrics_providers])}"
            )
        else:
            song.lyrics = lyrics

    def convert_with_ffmpeg(self, download_info, output_file, song, temp_file):
        bitrate: Optional[str] = (
            self.bitrate if self.bitrate else f"{int(download_info['abr'])}k"
        )
        # Ignore the bitrate if the preserve original audio
        # option is set to true
        if self.preserve_original_audio:
            bitrate = None
        success, result = convert(
            input_file=temp_file,
            output_file=output_file,
            ffmpeg=self.ffmpeg,
            output_format=self.output_format,
            bitrate=bitrate,
        )
        if not success and result:
            # If the conversion failed and there is an error message
            # create a file with the error message
            # and save it in the errors directory
            # raise an exception with file path
            file_name = (
                get_errors_path()
                / f"ffmpeg_error_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.txt"
            )

            error_message = ""
            for key, value in result.items():
                error_message += f"### {key}:\n{str(value).strip()}\n\n"

            with open(file_name, "w", encoding="utf-8") as error_path:
                error_path.write(error_message)

            # Remove the file that failed to convert
            if output_file.exists():
                output_file.unlink()

            raise FFmpegError(
                f"Failed to convert {song.display_name}, "
                f"you can find error here: {str(file_name.absolute())}"
            )
