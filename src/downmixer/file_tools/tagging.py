import logging
from urllib.request import urlopen

import mutagen
from mutagen.id3 import APIC, USLT, ID3

from src.downmixer.providers import Download

logger = logging.getLogger("downmixer").getChild(__name__)


def tag_download(download: Download):
    logger.info(f"Tagging file {download.filename}")
    easy_id3 = mutagen.File(download.filename, easy=True)

    logger.debug("Deleting old tag information")
    easy_id3.delete()

    logger.debug(f"Filling with info from attached song '{download.song.title}'")
    easy_id3["title"] = download.song.name
    easy_id3["titlesort"] = download.song.name
    easy_id3["artist"] = download.song.all_artists
    easy_id3["isrc"] = _return_if_valid(download.song.isrc)
    easy_id3["album"] = _return_if_valid(download.song.album.name)
    easy_id3["date"] = _return_if_valid(download.song.date)
    easy_id3["originaldate"] = _return_if_valid(download.song.date)
    easy_id3["albumartist"] = _return_if_valid(download.song.album.artists)
    easy_id3["tracknumber"] = [
        _return_if_valid(download.song.track_number),
        _return_if_valid(download.song.album.track_count),
    ]

    logger.info("Saving EasyID3 data to file")
    easy_id3.save()

    has_cover = download.song.album.images is not None and len(download.song.album.images) != 0
    if download.song.lyrics or has_cover:
        id3 = ID3(download.filename)

        if download.song.lyrics:
            logger.debug("Adding lyrics")
            id3["USLT::'eng'"] = USLT(
                encoding=3, lang="eng", desc="Unsynced Lyrics", text=download.song.lyrics
            )

        if has_cover:
            url = download.song.album.images[0]["url"]
            logger.debug(f"Downloading cover image from URL {url}")

            with urlopen(url) as raw_image:
                id3["APIC"] = APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,
                    desc="Cover",
                    data=raw_image.read(),
                )

        logger.info("Saving ID3 data to file")
        id3.save()
    # TODO: include all tags possible here, grab them from youtube/spotify if needed


def _return_if_valid(value):
    if value is None:
        return ""
    else:
        return value
