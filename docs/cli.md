# CLI

Downmixer's purpose is not to be an end-user command line tool like spotDL, youtubeDL and others. It's a Python library to automate syncing of music from Spotify using any provider of audio, lyrics and metadata.

That being said, Downmixer *does* provide a simple command line interface for convenience, testing and simple usage.

It uses the default [`BasicProcessor`](/reference/processing/#downmixer.processing.BasicProcessor) class to search, download and convert a Spotify track, playlist or album.

## Usage

````shell
downmixer [-h] [-o OUTPUT] [-c COOKIES] {download} id
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


