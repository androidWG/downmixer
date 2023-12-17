from pathlib import Path
from types import ModuleType

from downmixer.providers import _get_all_providers


def get_all_audio_providers() -> list[ModuleType]:
    return _get_all_providers(Path(__file__).parent.name)
