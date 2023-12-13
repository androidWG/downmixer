import requests

from library import Song
from providers import BaseLyricsProvider, ProviderSearchResult


class AZLyricsProvider(BaseLyricsProvider):
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

        # extract value from js code
        js_code = resp.text
        start_index = js_code.find('value"') + 9
        end_index = js_code[start_index:].find('");')

        self.x_code = js_code[start_index : start_index + end_index]

    def get_lyrics(self, result: ProviderSearchResult):
        artist_str = ", ".join(artist for artist in artists if artist)

        params = {
            "q": f"{artist_str} - {name}",
            "x": self.x_code,
        }

        response = self.session.get(
            "https://search.azlyrics.com/search.php", params=params
        )
        soup = BeautifulSoup(response.content, "html.parser")

        td_tags = soup.find_all("td")
        if len(td_tags) == 0:
            return None

        result = td_tags[0]

        a_tags = result.find_all("a", href=True)
        if len(a_tags) != 0:
            lyrics_url = a_tags[0]["href"]
        else:
            return None

        if lyrics_url.strip() == "":
            return None

        response = self.session.get(lyrics_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all divs that don't have a class
        div_tags = soup.find_all("div", class_=False, id_=False)

        # Find the div with the longest text
        lyrics_div = sorted(div_tags, key=lambda x: len(x.text))[-1]

        # extract lyrics from div and clean it up
        lyrics = lyrics_div.get_text().strip()

        return lyrics

    def search(self, song: Song):
        pass
