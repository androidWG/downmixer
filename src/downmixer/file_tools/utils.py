import re


def make_sane_filename(filename):
    return re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", filename)
