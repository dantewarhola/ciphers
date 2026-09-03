"""Atbash cipher: mirror the alphabet (A<->Z, B<->Y, ...).

Here mostly as a worked example of a second algorithm: no parameters, and
encrypt/decrypt are the same operation. Copy this file's shape when you add
your own.
"""

from .base import Cipher


def mirror(text, params=None):
    output = ""
    for char in text:
        if char.isupper():
            output += chr(90 - (ord(char) - 65))
        elif char.islower():
            output += chr(122 - (ord(char) - 97))
        else:
            output += char
    return output


def validate(text):
    if not text.strip():
        return "Input can't be empty."
    return None


CIPHER = Cipher(
    name="Atbash",
    description="Mirrors the alphabet. Running it twice gives you back the original.",
    encrypt=mirror,
    decrypt=mirror,
    validate=validate,
)