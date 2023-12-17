"""Classes and methods to easily compare the compatibility of a result with a song being matched. Uses fuzzy string
comparison with the [RapidFuzz package](https://github.com/maxbachmann/RapidFuzz).

Matching is done individually on song name, primary artist, other artists, album name, and length - artist matches are
calculated down to a single score value (scores go from 0 to 100). Therefore, the sum can be a range of 0 to 400.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional

from rapidfuzz import fuzz

import downmixer.matching.utils
from downmixer.library import Artist, Song


class MatchQuality(Enum):
    """Thresholds to consider when getting the quality of a match. Values are based on the sum of all matches - if
    all are perfect, equals to 400.

    ## Perfect `score over 390`
    Both songs are the same. Some lenience is given in case an artist isn't included in the artist list for example.

    ## Good `score over 280`
    Likely a different version of the same song, like a live version for example.

    ## Mediocre `score over 150`
    Probably a cover from another artist or something else from the same artist.

    ## Bad `score over 0`
    Not the same song.
    """

    PERFECT = 390
    GOOD = 280
    MEDIOCRE = 150
    BAD = 0


@dataclass
class MatchResult:
    """Holds match results and provides convenient property methods to get/calculate quality and match score."""

    method: str
    name_match: float
    artists_match: list[Tuple[Artist, float]]
    album_match: float
    length_match: float

    @property
    def quality(self) -> MatchQuality:
        """Returns the match quality from the enum `MatchQuality`."""
        result = MatchQuality.BAD
        for q in MatchQuality:
            if self.sum <= q.value:
                result = q

        return result

    @property
    def artists_match_avg(self) -> float:
        """Averages the match score of the list of artists. Returns zero if list is empty."""
        match_values = [x[1] for x in self.artists_match]
        if len(match_values) == 0:
            return 0.0
        else:
            return sum(match_values) / len(self.artists_match)

    @property
    def sum(self) -> float:
        """Sums all matches (uses average artist match value). Maximum value is 400."""
        return (
            self.name_match
            + self.artists_match_avg
            + self.album_match
            + self.length_match
        )

    def all_above_threshold(self, threshold: float) -> bool:
        """Checks if all the scores are above the threshold value given.

        Args:
            threshold (float): Tha value that will be compared to all the values.

        Returns:
            True if every match score is higher than the threshold, false otherwise.
        """
        name_test = self.name_match >= threshold
        artists_test = self.artists_match_avg >= threshold
        album_test = self.album_match >= threshold
        length_test = self.length_match >= threshold

        return name_test and artists_test and album_test and length_test


def match(original_song: Song, result_song: Song) -> MatchResult:
    """Returns match values using RapidFuzz comparing the two given song objects.

    Args:
        original_song (Song): Song to be compared to. Should be slugified for better results.
        result_song (Song): Song being compared. Should be slugified for better results.

    Returns:
        MatchResult: Match scores of the comparison between original and result song.
    """
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
    """Calculates match score for two strings. The second string can be None and will be treated as empty if such."""
    try:
        result = fuzz.WRatio(str1, str2 if str2 is not None else "")
        match_value = result
    except ValueError:
        match_value = 0.0
    return match_value


def _match_artist_list(
    slug_song: Song, slug_result: Song
) -> list[Tuple[Artist, float]]:
    """Uses _match_simple to calculate match score of all the artists from a song."""
    artist_matches = []
    for artist in slug_song.artists:
        highest_ratio: Tuple[Optional[Artist], float] = (None, -1.0)
        for result_artist in slug_result.artists:
            ratio = _match_simple(artist.name, result_artist.name)
            if ratio > highest_ratio[1]:
                highest_ratio = (artist, ratio)

        if highest_ratio[0] is not None:
            artist_matches.append(highest_ratio)

    return artist_matches


def _match_length(len1: float, len2: float, ceiling: int = 120):
    """Plots the difference between `len1` and `len2` in a [graph](https://www.desmos.com/calculator/3guvoyxg4z) and
    returns the y value of this graph. The `ceiling` parameter defines the scale of the x-axis.
    """
    x = downmixer.matching.utils.remap(abs(len1 - len2), 0, ceiling, 0, 1)
    y = downmixer.matching.utils.ease(x) * 100
    return max(min(100, int(y)), 0)
