<p align="center">
    <img src="https://raw.githubusercontent.com/androidWG/downmixer/main/docs/assets/logo_white.svg" style="width: 80vw; max-width: 650px"/>
</p>

Download Spotify songs easily using YouTube Music. Can be an alternative or replacement to [spotDL](https://github.com/spotDL/spotify-downloader), however, it is **only a Python library, *not* a CLI tool**. A very simple `download` command is available for convenience only.

## This project is currently in alpha version.

Basic functionality mostly works, but everything else doesn't. Also, no documentation.


## Usage
### Command line
```shell
downmixer download [spotify id]
```
Downloads the first matched result for a Spotify song ID.

### Use as a library
Downmixer is made to be adapted to your workflow. By default it doesn't provide a large convenience function like spotDL's `search()` and `download()` methods.

Documentation coming soon.

## Building

```shell
git clone https://github.com/androidWG/downmixer
cd downmixer
pipenv install
pip install build
```
