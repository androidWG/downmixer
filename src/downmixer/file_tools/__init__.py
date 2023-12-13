"""Code relating to the manipulation of files - converting and tagging audio files specifically."""

from enum import Enum


class Format(Enum):
    MP3 = "mp3"
    FLAC = "flac"
    WAV = "wav"
    OPUS = "opus"


# TODO: Deal with the fact there's like 5000 different combinations of this
# https://developer.mozilla.org/en-US/docs/Web/Media/Formats/codecs_parameter#mpeg-4_audio
class AudioCodecs(Enum):
    MP4A_40_5 = "mp4a.40.5"
    MP4A_40_2 = "mp4a.40.2"
    OPUS = "opus"
