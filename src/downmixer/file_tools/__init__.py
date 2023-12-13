from enum import Enum


class Format(Enum):
    MP3 = "mp3"
    FLAC = "flac"
    WAV = "wav"
    OPUS = "opus"


class AudioCodecs(Enum):
    MP4A_40_5 = "mp4a.40.5"
    OPUS = "opus"
