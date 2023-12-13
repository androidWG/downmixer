from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional

from rapidfuzz import fuzz

import matching.utils
from library import Artist, Song


class MatchQuality(Enum):
    """Thresholds to consider when getting the quality of a match. Values are based on the sum of all matches."""

    PERFECT = 390  # Both songs are the same. Some lenience is given in case an artist isn't included in the artist list for example.
    GOOD = 280  # Likely a different version of the same song, like a live version.
    MEDIOCRE = 150  # Probably a cover from another artist or something else from the same artist.
    BAD = 0  # Not the same song.


@dataclass
class MatchResult:
    method: str
    name_match: float
    artists_match: List[Tuple[Artist, float]]
    album_match: float
    length_match: float

    @property
    def quality(self) -> MatchQuality:
        result = MatchQuality.BAD
        for q in MatchQuality:
            if self.sum >= q.value:
                result = q

        return result

    @property
    def artists_match_avg(self) -> float:
        match_values = [x[1] for x in self.artists_match]
        return sum(match_values) / len(self.artists_match)

    @property
    def sum(self) -> float:
        return (
            self.name_match
            + self.artists_match_avg
            + self.album_match
            + self.length_match
        )

    def all_above_threshold(self, threshold: float) -> bool:
        name_test = self.name_match >= threshold
        artists_test = self.artists_match_avg >= threshold
        album_test = self.album_match >= threshold
        length_test = self.length_match >= threshold

        return name_test and artists_test and album_test and length_test


def match(original_song: Song, result_song: Song) -> MatchResult:
    song_slug = original_song.slug()
    result_slug = result_song.slug()

    name_match = _match_simple(song_slug.name, result_slug.name)
    artists_matches = _match_artist_list(song_slug, result_slug)
    if result_slug.album is not None:
        album_match = _match_simple(song_slug.album.name, result_slug.album.name)
    else:
        album_match = 0.0
    length_match = _match_length(original_song.duration, result_song.duration)

    return MatchResult(
        method="WRatio",
        name_match=name_match,
        artists_match=artists_matches,
        album_match=album_match,
        length_match=length_match,
    )


def _match_simple(str1: str, str2: str | None) -> float:
    try:
        result = fuzz.WRatio(str1, str2 if str2 is not None else "")
        match_value = result
    except ValueError:
        match_value = 0.0
    return match_value


def _match_artist_list(
    slug_song: Song, slug_result: Song
) -> List[Tuple[Artist, float]]:
    artist_matches = []
    for artist in slug_song.artists:
        highest_ratio: Tuple[Optional[Artist], float] = (None, 0.0)
        for result_artist in slug_result.artists:
            ratio = _match_simple(artist.name, result_artist.name)
            if ratio > highest_ratio[1]:
                highest_ratio = (artist, ratio)

        if highest_ratio[0] is not None:
            artist_matches.append(highest_ratio)

    return artist_matches


def _match_length(len1: float, len2):
    x = matching.utils.remap(abs(len1 - len2), 0, 120, 0, 1)
    return matching.utils.ease(x) * 100
