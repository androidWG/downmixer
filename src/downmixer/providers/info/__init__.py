import os
from types import ModuleType

from downmixer.providers import _get_all_providers


def get_all_info_providers() -> list[ModuleType]:
    return _get_all_providers(os.path.dirname(os.path.realpath(__file__)))
