import argparse
import asyncio
import logging
import os
import tempfile
from pathlib import Path

from downmixer import processing, log
from downmixer.spotify.utils import ResourceType, check_valid, get_resource_type

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
    "-o",
    "--output-folder",
    type=Path,
    default=os.curdir,
    dest="output",
    help="Path to the folder in which the final processed files will be placed.",
)
parser.add_argument(
    "-c",
    "--cookie-file",
    type=str,
    default=None,
    dest="cookies",
    help="Path to a Netscape-formatted text file containing cookies to be used in the requests to YouTube.",
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
            rtype = get_resource_type(args.id)

            processor = processing.BasicProcessor(
                args.output, temp, cookies=os.path.abspath(args.cookies)
            )
            if rtype == ResourceType.TRACK:
                logger.debug("Downloading one track")
                asyncio.run(processor.process_song(args.id))
            else:
                logger.debug("Downloading many tracks")
                loop = asyncio.new_event_loop()
                loop.run_until_complete(processor.process_playlist(args.id))
                loop.close()


if __name__ == "__main__":
    command_line()
