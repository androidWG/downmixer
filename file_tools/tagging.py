import logging
from urllib.request import urlopen

import mutagen
from mutagen.id3 import APIC, USLT, ID3

from matching import MatchQuality
from providers import Download

logger = logging.getLogger("downmixer").getChild(__name__)


def tag_download(download: Download):
    logger.info(f"Tagging file {download.filename}")
    easy_id3 = mutagen.File(download.filename, easy=True)

    logger.debug("Deleting old tag information")
    easy_id3.delete()

    if download.search_result.match.quality == MatchQuality.PERFECT:
        song = download.search_result.original_song
    else:
        song = download.search_result.result_song

    logger.debug(f"Filling with info from attached song '{song.title}'")
    easy_id3["title"] = song.name
    easy_id3["titlesort"] = song.name
    easy_id3["artist"] = song.all_artists
    easy_id3["isrc"] = _return_if_valid(song.isrc)
    easy_id3["album"] = _return_if_valid(song.album.name)
    easy_id3["date"] = _return_if_valid(song.date)
    easy_id3["originaldate"] = _return_if_valid(song.date)
    easy_id3["albumartist"] = _return_if_valid(song.album.artists)
    easy_id3["tracknumber"] = [
        _return_if_valid(song.track_number),
        _return_if_valid(song.album.track_count),
    ]

    logger.info("Saving EasyID3 data to file")
    easy_id3.save()

    has_cover = song.album.images is not None and len(song.album.images) != 0
    if song.lyrics or has_cover:
        id3 = ID3(download.filename)

        if song.lyrics:
            logger.debug("Adding lyrics")
            id3["USLT::'eng'"] = USLT(
                encoding=3, lang="eng", desc="Unsynced Lyrics", text=song.lyrics
            )

        if has_cover:
            url = song.album.images[0]["url"]
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
