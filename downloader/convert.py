import copy
import logging
import os
from pathlib import Path

from ffmpeg import FFmpeg

from providers import Download

logger = logging.getLogger("downmixer").getChild(__name__)


async def convert_download(
    downloaded: Download, delete_original: bool = True
) -> Download:
    logger.info("Starting conversion")

    # TODO: Check if file already exists
    output = str(downloaded.filename).replace(downloaded.filename.suffix, ".mp3")
    ffmpeg = (
        FFmpeg()
        .option("vn")
        .input(str(downloaded.filename))
        .output(output, {"b:a": "320k"})
    )

    @ffmpeg.on("start")
    def on_start(arguments):
        logger.debug("Arguments: " + ", ".join(arguments))

    @ffmpeg.on("stderr")
    def on_stderr(line):
        logger.debug(line)

    @ffmpeg.on("progress")
    def on_progress(progress):
        logger.info(progress)

    @ffmpeg.on("terminated")
    def on_terminated():
        logger.critical("ffmpeg was terminated!")

    @ffmpeg.on("error")
    def on_error(code):
        logger.error(f"ffmpeg error code {code}")

    logger.info("Running ffmpeg")
    await ffmpeg.execute()
    if delete_original:
        os.remove(downloaded.filename)

    logger.debug("Creating copy of download object")
    edited_download = copy.copy(downloaded)
    edited_download.filename = Path(output)
    return edited_download
