"""Registry of every cipher the GUI offers.

Any module in this folder that defines a module-level `CIPHER` is picked up
automatically. There is no list to maintain.

To add an algorithm:
  * Write ciphers/yourcipher.py exporting `CIPHER = Cipher(...)`.
    If the logic lives in a standalone script you'd rather not touch, write a
    thin adapter instead - see caesar_adapter.py for the pattern.

That's it. Files without a CIPHER are ignored, so helper modules can live here
too. Files that fail to import are reported in LOAD_ERRORS rather than taking
down the whole app.
"""

import importlib
import pkgutil

from .base import Action, Cipher, Param

__all__ = ["Action", "Cipher", "Param", "REGISTRY", "LOAD_ERRORS", "names", "get"]

REGISTRY = []
LOAD_ERRORS = []

# Modules that are infrastructure, not ciphers.
_SKIP = {"base"}


def _discover():
    for info in pkgutil.iter_modules(__path__):
        if info.name.startswith("_") or info.name in _SKIP:
            continue
        try:
            module = importlib.import_module(f"{__name__}.{info.name}")
        except Exception as exc:
            LOAD_ERRORS.append(f"{info.name}: {type(exc).__name__}: {exc}")
            continue

        cipher = getattr(module, "CIPHER", None)
        if isinstance(cipher, Cipher):
            REGISTRY.append(cipher)

    REGISTRY.sort(key=lambda cipher: cipher.name.lower())


_discover()


def names():
    return [cipher.name for cipher in REGISTRY]


def get(name):
    for cipher in REGISTRY:
        if cipher.name == name:
            return cipher
    raise KeyError(f"No cipher registered under {name!r}")