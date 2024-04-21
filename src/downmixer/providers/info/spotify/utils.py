from __future__ import annotations

import re

from downmixer.providers import ResourceType

resource_type_map = {
    ResourceType.SONG: "track",
    ResourceType.ALBUM: "album",
    ResourceType.PLAYLIST: "playlist",
    ResourceType.ARTIST: "artist",
}


def get_resource_type(value: str) -> ResourceType | None:
    if not check_valid(value):
        return None

    pattern = r"spotify(?:.com)?(?::|\/)(\w*)(?::|\/)(?:\w{20,24})"
    matches = re.search(pattern, value)

    if matches is None:
        return None
    else:
        return list(resource_type_map.keys())[
            list(resource_type_map.values()).index(matches.group(1).lower())
        ]


def check_valid(value: str, type_filter: list[ResourceType] = None) -> bool:
    """Checks using a regex if a string is a valid Spotify ID, URI or URL.

    Args:
        value (str): Arbitrary string that will be checked.
        type_filter (list[ResourceType]): Which resource types are accepted. Default any type.

    Returns:
         bool: True if the string given through `value` is a valid Spotify ID, URI or URL **and** it matches **any**
         of the specified resource types. Otherwise, returns False.
    """
    if type_filter is None:
        type_filter = [e for e in ResourceType]

    for t in type_filter:
        regex = r"spotify.*" + resource_type_map[t] + r"(?::|\/)(\w{20,24})"
        if re.search(regex, value) is not None:
            return True

    return False
