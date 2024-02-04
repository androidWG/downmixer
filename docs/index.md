# Getting started

## Commands
Downmixer is a library first. The `download` command specified below is purely for testing and convenience.

* `downmixer download [spotify-id]` - Download a Spotify song to the current directory.

## Overview
Downmixer is divided into a few packages that cover the basic process of getting a song info from Spotify, downloading, converting it and tagging it to be used in a library. These are:

 - `file_tools` - converting and tagging
 - `matching` - matching results from providers to the Spotify song
- `providers` - info, audio and lyrics providers
 - `processing` - sample/convenience class to download one or more files - used by the [command line tool](cli.md)

These packages are all independent and are expected to be implemented by you for whatever requirements your application has.

### Providers

Every piece of data gathered from a service is done through **providers** to provide maximum expandability in what
services Downmixer is compatible with. Every provider can have custom options and should be managed by your application.

Providers must be classes derived from `BaseInfoProvider`, `BaseAudioProvider` and `BaseLyricsProvider` to be used and
found by Downmixer. These base classes provide async search and download methods that must be overridden.

#### Info Providers

Bundled: `SpotifyInfoProvider`

Where the songs will be searched and (preferably, but not enforced by Downmixer) where the information for the final
file's ID3 tags will be sourced from.

#### Audio Providers

Bundled: `YouTubeMusicAudioProvider`

Where the audio file will be downloaded from.

### File Tools
This package uses [FFmpeg](https://ffmpeg.org/) and [Mutagen](https://github.com/quodlibet/mutagen) to convert and tag downloaded files respectively.
