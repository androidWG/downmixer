# CLI

Downmixer's purpose is not to be an end-user command line tool like spotDL, youtubeDL and others. It's a Python library
to automate syncing of music from any music library, audio, and lyrics platform.

That being said, Downmixer *does* provide a simple command line interface for convenience, testing and simple usage.

It uses the default [`BasicProcessor`](/reference/processing/#downmixer.processing.BasicProcessor) class to search,
download and convert a song, playlist or album. It uses the bundled `SpotifyInfoProvider`, meaning the `id` value must
be a valid Spotify track, album or playlist ID.

## Usage

````shell
downmixer [OPTIONS] {COMMAND}

````

### Positional arguments
- `command` 
  - Command to execute. Currently, the only option is `download`.
- `id` 
  - A valid Spotify ID, URI or URL for a track, album or playlist.

### Options
- `-h, --help` 
  - Show the help message
- `-o OUTPUT, --output-folder OUTPUT`
  - Path to the folder in which the final processed files will be placed. By default, this is the current working directory.
- `-c COOKIES, --cookie-file COOKIES`
  - Path to a Netscape-formatted text file containing cookies to be used in the requests to YouTube.
- `-ip {SpotifyInfoProvider}, --info-provider {SpotifyInfoProvider}`
  - Info provider extending BaseInfoProvider to use. Defaults to 'SpotifyInfoProvider'.
- `-ap {YouTubeMusicAudioProvider}, --audio-provider {YouTubeMusicAudioProvider}`
  - Audio provider extending BaseAudioProvider to use. Defaults to 'YouTubeMusicAudioProvider'.
- `-lp {AZLyricsProvider}, --lyrics-provider {AZLyricsProvider}`
  - Lyrics provider extending BaseLyricsProvider to use. Defaults to 'AZLyricsProvider'.



