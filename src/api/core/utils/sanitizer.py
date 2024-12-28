# -*- coding: utf-8 -*-

import re
import html
from urllib.parse import quote

from pydantic import validate_arguments

from .validator import SpecialCharsRegEnum


@validate_arguments
def escape_html(val: str) -> str:
    """Escape HTML characters.

    Args:
        val (str, required): String to escape.

    Returns:
        str: Escaped string.
    """

    _escaped = html.escape(val)
    return _escaped


@validate_arguments
def espace_url(val: str) -> str:
    """Escape URL characters.

    Args:
        val (str, required): String to escape.

    Returns:
        str: Escaped string.
    """

    _escaped = quote(val)
    # _escaped = quote_plus(val)
    return _escaped


@validate_arguments
def sanitize_special_chars(val: str, mode: str = "DEFAULT") -> str:
    """Sanitize special characters.

    Args:
        val  (str, required): String to sanitize.
        mode (str, optional): Sanitization mode. Defaults to "DEFAULT".

    Returns:
        str: Sanitized string.
    """

    _pattern = r""
    mode = mode.strip().upper()
    if (mode == "BASE") or (mode == "HTML"):
        _pattern = SpecialCharsRegEnum.BASE.value
    elif (mode == "LOW") or (mode == "BASIC") or (mode == "DEFAULT"):
        _pattern = SpecialCharsRegEnum.LOW.value
    elif mode == "MEDIUM":
        _pattern = SpecialCharsRegEnum.MEDIUM.value
    elif (
        (mode == "HIGH")
        or (mode == "SCRIPT")
        or (mode == "STRONG")
        or (mode == "SQL")
        or (mode == "INJECTION")
    ):
        _pattern = SpecialCharsRegEnum.HIGH.value
    elif (mode == "ADVANCED") or (mode == "STRICT"):
        _pattern = SpecialCharsRegEnum.ADVANCED.value

    _sanitized = re.sub(pattern=_pattern, repl="", string=val)
    return _sanitized


__all__ = [
    "escape_html",
    "espace_url",
    "sanitize_special_chars",
]
