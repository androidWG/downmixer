from library import Song, Artist, Album
from providers.audio.youtube_music import YouTubeMusicAudioProvider


def test_search():
    song = Song(
        name="soft spot",
        artists=[Artist(name="piri"), Artist(name="Tommy Villiers")],
        album=Album(name="froge.mp3"),
        duration=220,
        isrc="QZHN52145683",
        uri="spotify:track:1mtLhZXbQqeU3qugQkuwhk",
        url="https://open.spotify.com/track/1mtLhZXbQqeU3qugQkuwhk"
    )

    provider = YouTubeMusicAudioProvider()
    results = provider.search(song)
    print(results)


if __name__ == '__main__':
    test_search()

