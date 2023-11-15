# -*- coding: utf-8 -*-

from typing import Tuple
from urllib import request
from http import HTTPStatus
from http.client import HTTPResponse

import aiohttp
from fastapi import Request
from pydantic import conint, validate_arguments


@validate_arguments
def get_http_status(status_code: conint(ge=100, le=599)) -> Tuple[HTTPStatus, bool]:
    """Get HTTP status code enum from integer value.

    Args:
        status_code (int, required): Status code for HTTP response: [100 <= status_code <= 599].

    Raises:
        ValueError: If status code is not in range [100 <= status_code <= 599].

    Returns:
        Tuple[HTTPStatus, bool]: Tuple of HTTP status code enum and boolean value if status code is known.
    """

    _http_status: HTTPStatus
    _is_known_status = False
    try:
        _http_status = HTTPStatus(status_code)
        _is_known_status = True
    except ValueError:
        if (100 <= status_code) and (status_code < 200):
            status_code = 100
        elif (200 <= status_code) and (status_code < 300):
            status_code = 200
        elif (300 <= status_code) and (status_code < 400):
            status_code = 304
        elif (400 <= status_code) and (status_code < 500):
            status_code = 400
        elif (500 <= status_code) and (status_code < 600):
            status_code = 500
        else:
            raise ValueError(f"Invalid HTTP status code: '{status_code}'!")

        _http_status = HTTPStatus(status_code)

    return (_http_status, _is_known_status)


@validate_arguments(config=dict(arbitrary_types_allowed=True))
def get_request_path(request: Request) -> str:
    """Get request path with query params.

    Args:
        request (Request, required): Request object.

    Returns:
        str: Request path.
    """

    _url_path = request.url.path
    if request.url.query:
        _url_path += "?" + request.url.query
    return _url_path


@validate_arguments
def is_connectable(
    url: str = "https://www.google.com", timeout: int = 3, check_status=False
) -> bool:
    """Check if the url is connectable.

    Args:
        url          (str , optional): URL to check. Defaults to 'https://www.google.com'.
        timeout      (int , optional): Timeout in seconds. Defaults to 3.
        check_status (bool, optional): Check HTTP status code (200). Defaults to False.

    Returns:
        bool: True if connectable, False otherwise.
    """

    try:
        _response: HTTPResponse = request.urlopen(url, timeout=timeout)
        if check_status:
            return _response.getcode() == 200
        return True
    except:
        return False


@validate_arguments
async def async_is_connectable(
    url: str = "https://www.google.com", timeout: int = 3, check_status=False
) -> bool:
    """Check if the url is connectable.

    Args:
        url          (str , optional): URL to check. Defaults to 'https://www.google.com'.
        timeout      (int , optional): Timeout in seconds. Defaults to 3.
        check_status (bool, optional): Check HTTP status code (200). Defaults to False.

    Returns:
        bool: True if connectable, False otherwise.
    """

    try:
        async with aiohttp.ClientSession() as _session:
            async with _session.get(url, timeout=timeout) as _response:
                if check_status:
                    return _response.status == 200
                return True
    except:
        return False


__all__ = [
    "get_http_status",
    "get_request_path",
    "is_connectable",
    "async_is_connectable",
]
