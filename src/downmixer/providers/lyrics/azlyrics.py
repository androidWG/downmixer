from typing import Optional

import requests
from bs4 import BeautifulSoup, Comment, ResultSet

from downmixer import matching
from downmixer.library import Song, Artist
from downmixer.providers import BaseLyricsProvider, LyricsSearchResult

COPYRIGHT_DISCLAIMER = (
    "Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our "
    "licensing agreement. Sorry about that."
)


def search_result_from_azlyrics(
    result: ResultSet, original_song: Song
) -> LyricsSearchResult:
    """Create a LyricsSearchResult instance from a
    [Beautiful Soup 4 `ResultSet`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all) from AZLyrics.

    Args:
        result (bs4.ResultSet):
        original_song (Song): Instance of a song from Spotify that will be compared against this search result.

    Returns:
        LyricsSearchResult from AZLyrics.
    """
    strings = result[0].find_all("b")
    name = strings[0].text[1:-1]
    artist = strings[1].text

    result_song = Song(name=name, artists=[Artist(name=artist)])
    return LyricsSearchResult(
        provider="azlyrics",
        match=matching.match(original_song, result_song),
        name=name,
        artist=artist,
        url=result[0]["href"],
    )


class AZLyricsProvider(BaseLyricsProvider):
    provider_name = "azlyrics"

    def __init__(self):
        headers = {
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "en-US;q=0.8,en;q=0.7",
        }

        self.session = requests.Session()
        self.session.headers.update(headers)

        resp = self.session.get("https://www.azlyrics.com/geo.js")

        js_code = resp.text
        start_index = js_code.find('value"') + 9
        end_index = js_code[start_index:].find('");')

        self.x_code = js_code[start_index : start_index + end_index]

    async def get_lyrics(self, search_result: LyricsSearchResult) -> Optional[str]:
        response = self.session.get(search_result.url)
        soup = BeautifulSoup(response.content, "html.parser")

        div_tags = soup.find_all("div", class_=False, id_=False)
        for d in div_tags:
            comments = d.find_all(string=lambda x: isinstance(x, Comment))
            # All AZLyrics lyrics pages have this disclaimer as an HTML comment on the top of the div
            # containing the lyrics. We can use it to identify which div has lyrics.
            if len(comments) != 0 and COPYRIGHT_DISCLAIMER in comments[0]:
                lyrics_div = d
                lyrics = lyrics_div.get_text().strip()
                return lyrics

        return None

    async def search(self, song: Song) -> Optional[list[LyricsSearchResult]]:
        params = {"q": song.full_title, "x": self.x_code, "w": "songs"}

        response = self.session.get(
            "https://search.azlyrics.com/search.php", params=params
        )
        soup = BeautifulSoup(response.content, "html.parser")

        td_tags = soup.find_all("td")
        if len(td_tags) == 0:
            return None

        results: list[LyricsSearchResult] = []
        result_list = [x.find_all("a", href=True) for x in td_tags]
        for r in result_list:
            if len(r) == 0:
                continue
            # The first and last td tags in AZLyrics have the page buttons. Skip those when we meet them.
            elif r[0].has_attr("class") and "btn" in r[0]["class"]:
                continue
            else:
                results.append(search_result_from_azlyrics(r, song))

        ordered_results = sorted(results, reverse=True, key=lambda x: x.match.sum)

        return ordered_results


def instance():
    return AZLyricsProvider
