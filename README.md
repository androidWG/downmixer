<p style="text-align: center">
    <img alt="Downmixer logo" src="https://raw.githubusercontent.com/neufter/downmixer/main/docs/assets/logo_white.svg" style="width: 80vw; max-width: 650px"/>
</p>

Download songs from streaming services easily. Can be an alternative or replacement
to [spotDL](https://github.com/spotDL/spotify-downloader), however, it is **only a Python library, *not* a CLI tool**. A
very simple `download` command is available for convenience and testing only.

It is structured to be platform independent - by default, it syncs Spotify libraries downloaded from either or YouTube Music, with lyrics from AZLyrics. However, it can be extended to sync from any streaming service using
any audio file source, and any lyrics provider.

## This project is currently in alpha version.

Basic functionality works, with Spotify libraries and YT Music audio sources.

## Installation

Install the package with:
```shell
pip install downmixer
```

## Usage

### Command line

```shell
downmixer download [spotify id]
```

Downloads the first matched result for a Spotify song ID. Use `downmixer -h` for all options or refer to our [documentation](https://neufter.github.io/downmixer/cli).

### Use as a library

Downmixer is made to be used as a library by other apps, not by end users - its purpose is to abstract searching and downloading songs to make extensible apps. By creating classes inheriting `BaseInfoProvider`, `BaseAudioProvider`, and `BaseLyricsProvider` you can adapt Downmixer to use any kind of source for track info, audio and lyrics.

If you want to use Downmixer in your project, refer to the documentation here: https://neufter.github.io/downmixer/

## Building

Uses [uv](https://docs.astral.sh/uv/) package manager. To build from source, run:

```shell
git clone https://github.com/neufter/downmixer
cd downmixer
uv build
```
