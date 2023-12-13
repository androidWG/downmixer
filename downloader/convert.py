import os
from pathlib import Path

from ffmpeg import FFmpeg

from providers import Download


async def convert(downloaded: Download, delete_original: bool = True) -> Path:
    # TODO: Check if file already exists
    output = str(downloaded.filename).replace(downloaded.filename.suffix, ".mp3")
    ffmpeg = (
        FFmpeg()
        .option("vn")
        .input(str(downloaded.filename))
        .output(output, {"b:a": "320k"})
    )

    await ffmpeg.execute()
    if delete_original:
        os.remove(downloaded.filename)

    return Path(output)
