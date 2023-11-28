# -*- coding: utf-8 -*-

import re
from enum import Enum
from typing import List

from pydantic import validate_arguments


class ValidRegEnum(Enum):
    ALPHANUM = r"^[a-zA-Z0-9]+$"
    ALPHANUM_HYPHEN = r"^[a-zA-Z0-9_\-]+$"
    ALPHANUM_EXTEND = r"^[a-zA-Z0-9_\- .]+$"
    REQUEST_ID = (
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b|"
        r"\b[0-9a-fA-F]{32}\b"
    )


class SpecialCharsRegEnum(Enum):
    BASE = r"[&\\\/'\"<>]"
    LOW = r"[&\\\/'\"<>`{}|]"
    MEDIUM = r"[&\\\/'\"<>`{}|()\[\]]"
    HIGH = r"[&\\\/'\"<>`{}|()\[\]!@#$%^*;:?]"
    ADVANCED = r"[&\\\/'\"<>`{}|()\[\]~!@#$%^*_=\-+;:,.?\t\n ]"


@validate_arguments
def is_alphanum(val: str) -> bool:
    """Check if the string is alphanumeric.

    Args:
        val (str, required): String to check.

    Returns:
        bool: True if the string is alphanumeric, False otherwise.
    """

    _is_valid = bool(re.match(pattern=ValidRegEnum.ALPHANUM.value, string=val))
    return _is_valid


@validate_arguments
def is_alphanum_hyphen(val: str) -> bool:
    """Check if the string is alphanumeric with space, underscore, dot and dash/hyphen.

    Args:
        val (str, required): String to check.

    Returns:
        bool: True if the string is alphanumeric with space, underscore, dot and dash/hyphen, False otherwise.
    """

    _is_valid = bool(re.match(pattern=ValidRegEnum.ALPHANUM_HYPHEN.value, string=val))
    return _is_valid


@validate_arguments
def is_alphanum_extend(val: str) -> bool:
    """Check if the string is alphanumeric with space, underscore, dot and dash/hyphen.

    Args:
        val (str, required): String to check.

    Returns:
        bool: True if the string is alphanumeric with space, underscore, dot and dash/hyphen, False otherwise.
    """

    _is_valid = bool(re.match(pattern=ValidRegEnum.ALPHANUM_EXTEND.value, string=val))
    return _is_valid


@validate_arguments
def is_request_id(val: str) -> bool:
    """Check if the string is valid request ID.

    Args:
        val (str, required): String to check.

    Returns:
        bool: True if the string is valid request ID, False otherwise.
    """

    _is_valid = bool(re.match(pattern=ValidRegEnum.REQUEST_ID, string=val))
    return _is_valid


@validate_arguments
def is_blacklisted(val: str, blacklist: List[str]) -> bool:
    """Check if the string is blacklisted.

    Args:
        val       (str      , required): String to check.
        blacklist (List[str], required): List of blacklisted strings.

    Returns:
        bool: True if the string is blacklisted, False otherwise.
    """

    for _blacklisted in blacklist:
        if _blacklisted in val:
            return True

    return False


@validate_arguments
def is_valid(val: str, pattern: str) -> bool:
    """Check if the string is valid with given pattern.

    Args:
        val     (str, required): String to check.
        pattern (str, required): Pattern regex to check.

    Returns:
        bool: True if the string is valid with given pattern, False otherwise.
    """

    _is_valid = bool(re.match(pattern=pattern, string=val))
    return _is_valid


@validate_arguments
def has_special_chars(val: str, mode: str = "DEFAULT") -> bool:
    """Check if the string has special characters.

    Args:
        val  (str, required): String to check.
        mode (str, optional): Check mode. Defaults to "DEFAULT".

    Returns:
        bool: True if the string has special characters, False otherwise.
    """

    _has_special_chars = False

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

    _has_special_chars = bool(re.search(pattern=_pattern, string=val))
    return _has_special_chars


__all__ = [
    "ValidRegEnum",
    "SpecialCharsRegEnum",
    "is_alphanum",
    "is_alphanum_hyphen",
    "is_alphanum_extend",
    "is_request_id",
    "is_valid",
    "has_special_chars",
]
