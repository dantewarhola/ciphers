"""Wraps the stock caesar.py so the GUI can drive it.

caesar.py is not edited - it's imported as a sibling module and called as-is,
so it still runs on its own with `python ciphers/caesar.py`. This file only
translates between the GUI's calling convention, (text, params) -> str, and
the signatures caesar.py already has.

The one piece of real work is brute force: brute_force_decrypt prints its
results and returns None, so we capture stdout to get the text back.
"""

import io
from contextlib import redirect_stdout

from . import caesar
from .base import Action, Cipher, Param


def encrypt(text, params):
    return caesar.encrypt_text(text, params["key"])


def decrypt(text, params):
    return caesar.decrypt_text(text, params["key"])


def brute_force(text, params):
    """Run caesar.py's brute forcer and hand back what it printed."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        caesar.brute_force_decrypt(text)
    return buffer.getvalue().strip("\n")


def validate(text):
    """Same rules as caesar.py's get_text, minus the input() loop.

    is_allowed comes straight from caesar.py, so if you change the accepted
    character set there, the GUI follows automatically.
    """
    if not text.strip():
        return "Input can't be empty."

    rejected = sorted({char for char in text if not caesar.is_allowed(char)})
    if rejected:
        shown = " ".join(repr(char) for char in rejected)
        return f"Letters and spaces only. Remove these: {shown}"

    return None


CIPHER = Cipher(
    name="Caesar",
    description="Shifts each letter by a fixed number of places.",
    encrypt=encrypt,
    decrypt=decrypt,
    validate=validate,
    params=[Param(key="key", label="Key", kind="int", default="3")],
    extra_actions=[
        Action(label="Brute force", run=brute_force, uses_params=False),
    ],
)