import mutagen

from providers import Download


def tag_download(download: Download):
    file = mutagen.File(download.filename, easy=True)
    file.delete()

    song = download.search_result.original_song
    file["title"] = song.name
    file["titlesort"] = song.name
    file["tracknumber"] = [song.track_number, song.album.track_count]
    file["artist"] = song.artists
    file["album"] = song.album.name
    file["albumartist"] = song.album.artists
    file["date"] = song.date
    file["originaldate"] = song.date

    file.save()
