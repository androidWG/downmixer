import shutil
from pathlib import Path

from downmixer.file_tools import tag, utils
from downmixer.file_tools.convert import Converter
from downmixer.providers import Download
from downmixer.providers.audio.youtube_music import YouTubeMusicAudioProvider
from downmixer.providers.lyrics.azlyrics import AZLyricsProvider
from downmixer.spotify import SpotifyClient


async def _convert_download(download: Download) -> Download:
    converter = Converter(download)
    return await converter.convert()


class BasicProcessor:
    def __init__(self, output_folder: str, temp_folder: str):
        """Basic processing class to search a specific Spotify song and download it, using the default YT Music and
        AZLyrics providers.

        Args:
            output_folder (str): Folder path where the final file will be placed.
            temp_folder (str): Folder path where temporary files will be placed and removed from when processing
                is finished.
        """
        self.output_folder: Path = Path(output_folder)
        self.temp_folder = temp_folder

        scope = "user-library-read,playlist-read-private"
        self.spotify = SpotifyClient(scope)

        self.ytmusic = YouTubeMusicAudioProvider()
        self.azlyrics = AZLyricsProvider()

    async def _get_lyrics(self, download: Download):
        lyrics_results = await self.azlyrics.search(download.song)
        if lyrics_results is not None:
            lyrics = await self.azlyrics.get_lyrics(lyrics_results[0].url)
            download.song.lyrics = lyrics

    async def process_song(self, song_id: str):
        """Searches the song ISRC on YouTube

        Args:
            song_id (str): Valid ID, URI or URL of a Spotify track.
        """
        song = self.spotify.song(song_id)

        result = await self.ytmusic.search(song)
        downloaded = await self.ytmusic.download(result[0], self.temp_folder)
        converted = await _convert_download(downloaded)

        await self._get_lyrics(converted)
        tag.tag_download(converted)

        new_name = (
            utils.make_sane_filename(converted.song.title) + converted.filename.suffix
        )
        shutil.move(converted.filename, self.output_folder.joinpath(new_name))
