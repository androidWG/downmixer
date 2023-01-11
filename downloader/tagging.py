import logging

import mutagen

from providers import Download

logger = logging.getLogger("downmixer").getChild(__name__)


def tag_download(download: Download):
    logger.info(f"Tagging file {download.filename}")
    file = mutagen.File(download.filename, easy=True)

    logger.debug("Deleting old tag information")
    file.delete()

    song = download.search_result.original_song
    logger.debug(f"Filling with info from attached song '{song.title}'")
    file["title"] = song.name
    file["titlesort"] = song.name
    file["tracknumber"] = [song.track_number, song.album.track_count]
    file["artist"] = song.artists
    file["album"] = song.album.name
    file["albumartist"] = song.album.artists
    file["date"] = song.date
    file["originaldate"] = song.date

    logger.info("Saving tag data to file")
    file.save()
