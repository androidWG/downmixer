# Getting started

## Commands
Downmixer is a library first. The `download` command specified below is purely for testing and convenience.

* `downmixer download [spotify-id]` - Download a Spotify song to the current directory.

## Overview
Downmixer is divided into a few packages that cover the basic process of getting a song info from Spotify, downloading, converting it and tagging it to be used in a library. These are:

 - `file_tools` - converting and tagging
 - `matching` - matching results from providers to the Spotify song
 - `providers` - audio and lyrics providers
 - `spotify` - wrapper class for the [spotipy](https://github.com/spotipy-dev/spotipy) library
 - `processing` - sample/convenience class to download one or more files - used by the [command line tool](cli.md)

These packages are all independent and are expected to be implemented by you for whatever requirements your application has.

### Providers
Providers are divided by **audio providers** and **lyrics providers**. They each have a base class `BaseAudioProvider` and `BaseLyricsProvider` respectively, which must be implemented by all providers to be able to be used by Downmixer.

The base classes provide async search and a download methods that are overriden to provide functionality.

### File Tools
This package uses [FFmpeg](https://ffmpeg.org/) and [Mutagen](https://github.com/quodlibet/mutagen) to convert and tag downloaded files respectively.
