import argparse
import asyncio
import logging
import os
import tempfile
from pathlib import Path

from downmixer import processing, log
from downmixer.spotify.utils import ResourceType, check_valid

logger = logging.getLogger("downmixer").getChild(__name__)

parser = argparse.ArgumentParser(
    prog="downmixer", description="Easily sync tracks from Spotify."
)
parser.add_argument("procedure", choices=["download"])
parser.add_argument(
    "id",
    help="A valid Spotify ID, URI or URL for a track, album or playlist.",
)
parser.add_argument(
    "-o", "--output-folder", type=Path, default=os.curdir, dest="output"
)
args = parser.parse_args()


def command_line():
    log.setup_logging(debug=True)

    if args.procedure == "download":
        logger.debug("Running download command")

        if not check_valid(
            args.id,
            [ResourceType.TRACK, ResourceType.PLAYLIST, ResourceType.ALBUM],
        ):
            raise ValueError("id provided isn't valid")

        with tempfile.TemporaryDirectory() as temp:
            logger.debug(f"temp folder: {temp}")
            processor = processing.BasicProcessor(args.output, temp)
            asyncio.run(processor.process_song(args.id))


if __name__ == "__main__":
    command_line()
