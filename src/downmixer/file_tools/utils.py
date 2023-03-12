import re


def make_sane_filename(filename: str) -> str:
    """Removed common illegal characters from names, especially for Windows.

    Args:
        filename (str): Filename to be processed

    Returns:
        result (str): Filename with illegal characters replaced with '-'.
    """
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", filename)
