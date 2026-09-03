"""Shared types every cipher describes itself with.

The GUI never hard-codes anything about a specific algorithm. It reads the
Cipher object a module exports and builds its controls from that.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class Param:
    """One input the GUI should render for this cipher (a key, a keyword...)."""

    key: str                 # dict key handed to encrypt/decrypt
    label: str               # what the user sees
    kind: str = "text"       # "text" or "int"
    default: str = ""
    required: bool = True


@dataclass
class Action:
    """An extra button beyond Encrypt/Decrypt.

    Set uses_params=False for things like brute force that ignore the key
    boxes entirely - the GUI then won't complain about an empty or malformed
    key before running it.
    """

    label: str
    run: Callable[[str, dict], str]
    uses_params: bool = True


@dataclass
class Cipher:
    """Everything the GUI needs to know about one algorithm."""

    name: str
    encrypt: Callable[[str, dict], str]
    decrypt: Callable[[str, dict], str]
    description: str = ""
    params: List[Param] = field(default_factory=list)

    # Optional. Return an error string if the text can't be processed, else None.
    validate: Optional[Callable[[str], Optional[str]]] = None

    # Optional extras beyond encrypt/decrypt. Each one gets its own button.
    extra_actions: List[Action] = field(default_factory=list)

    def coerce_params(self, raw: Dict[str, str]) -> dict:
        """Turn the raw strings from the GUI entry boxes into real values."""
        values = {}
        for param in self.params:
            text = raw.get(param.key, "").strip()
            if param.kind == "int":
                try:
                    values[param.key] = int(text)
                except ValueError:
                    raise ValueError(
                        f"{param.label}: '{text}' isn't a whole number. "
                        "Enter something like 3 or -5."
                    )
            else:
                if param.required and not text:
                    raise ValueError(f"{param.label} can't be empty.")
                values[param.key] = text
        return values