import logging
from urllib.request import urlopen

import mutagen
from mutagen.id3 import APIC, USLT

from matching import MatchQuality
from providers import Download

logger = logging.getLogger("downmixer").getChild(__name__)


def tag_download(download: Download):
    logger.info(f"Tagging file {download.filename}")
    file = mutagen.File(download.filename, easy=True)

    logger.debug("Deleting old tag information")
    file.delete()

    if download.search_result.match.quality == MatchQuality.PERFECT:
        song = download.search_result.original_song
    else:
        song = download.search_result.result_song

    logger.debug(f"Filling with info from attached song '{song.title}'")
    file["title"] = song.name
    file["titlesort"] = song.name
    file["artist"] = song.all_artists
    file["album"] = _return_if_valid(song.album.name)
    file["date"] = _return_if_valid(song.date)
    file["originaldate"] = _return_if_valid(song.date)
    file["albumartist"] = _return_if_valid(song.album.artists)
    file["tracknumber"] = [
        _return_if_valid(song.track_number),
        _return_if_valid(song.album.track_count),
    ]

    if song.lyrics:
        file["USLT::'eng'"] = USLT(
            encoding=3, lang="eng", desc="desc", text=song.lyrics
        )

    if song.album.images and len(song.album.images) != 0:
        url = song.album.images[0]["url"]
        logger.debug(f"Downloading cover image from URL {url}")

        with urlopen(url) as raw_image:
            file["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=raw_image.read(),
            )
    # TODO: include all tags possible here, grab them from youtube/spotify if needed

    logger.info("Saving tag data to file")
    file.save()


def _return_if_valid(value):
    if value is None:
        return ""
    else:
        return value
