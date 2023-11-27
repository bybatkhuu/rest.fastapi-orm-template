# -*- coding: utf-8 -*-

from typing import Union
from datetime import datetime, timezone, tzinfo
from zoneinfo import ZoneInfo

from pydantic import validate_arguments

from beans_logging import logger

from src.core.constants import WarnEnum


@validate_arguments(config=dict(arbitrary_types_allowed=True))
def add_tzinfo(dt: datetime, tz: Union[ZoneInfo, tzinfo, str]) -> datetime:
    """Add or replace timezone info to datetime object.

    Args:
        dt (datetime                    , required): Datetime object.
        tz (Union[ZoneInfo, tzinfo, str], required): Timezone info.

    Returns:
        datetime: Datetime object with timezone info.
    """

    if isinstance(tz, str):
        tz = ZoneInfo(tz)

    dt = dt.replace(tzinfo=tz)
    return dt


@validate_arguments
def datetime_to_iso(
    dt: datetime, sep: str = "T", warn_mode: WarnEnum = WarnEnum.IGNORE
) -> str:
    """Convert datetime object to ISO 8601 format.

    Args:
        dt        (datetime, required): Datetime object.
        sep       (str     , optional): Separator between date and time. Defaults to "T".
        warn_mode (WarnEnum, optional): Warning mode. Defaults to WarnEnum.IGNORE.

    Returns:
        str: Datetime string in ISO 8601 format.
    """

    if not dt.tzinfo:
        _message = "Not found any timezone info in `dt` argument, assuming it's UTC timezone..."
        if warn_mode == WarnEnum.ALWAYS:
            logger.warning(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)
        elif warn_mode == WarnEnum.ERROR:
            _message = "Not found any timezone info in `dt` argument!"
            logger.error(_message)
            raise ValueError(_message)

        dt = add_tzinfo(dt=dt, tz="UTC")

    _dt_str = dt.isoformat(sep=sep, timespec="milliseconds")
    return _dt_str


@validate_arguments(config=dict(arbitrary_types_allowed=True))
def convert_tz(
    dt: datetime,
    tz: Union[ZoneInfo, tzinfo, str],
    warn_mode: WarnEnum = WarnEnum.ALWAYS,
) -> datetime:
    """Convert datetime object to another timezone.

    Args:
        dt        (datetime                    , required): Datetime object to convert.
        tz        (Union[ZoneInfo, tzinfo, str], required): Timezone info to convert.
        warn_mode (WarnEnum                    , optional): Warning mode. Defaults to WarnEnum.ALWAYS.

    Raises:
        ValueError: If `dt` argument doesn't have any timezone info and `warn_mode` is set to WarnEnum.ERROR.

    Returns:
        datetime: Datetime object which has been converted to another timezone.
    """

    if not dt.tzinfo:
        _message = "Not found any timezone info in `dt` argument, assuming it's UTC timezone..."
        if warn_mode == WarnEnum.ALWAYS:
            logger.warning(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)
        elif warn_mode == WarnEnum.ERROR:
            _message = "Not found any timezone info in `dt` argument!"
            logger.error(_message)
            raise ValueError(_message)

        dt = add_tzinfo(dt=dt, tz="UTC")

    if isinstance(tz, str):
        tz = ZoneInfo(tz)

    dt = dt.astimezone(tz=tz)
    return dt


@validate_arguments
def now_utc_tz() -> datetime:
    """Get current datetime in UTC timezone with tzinfo.

    Returns:
        datetime: Current datetime in UTC timezone with tzinfo.
    """

    _utc_dt = datetime.now(tz=timezone.utc)
    return _utc_dt


@validate_arguments
def now_local_tz() -> datetime:
    """Get current datetime in local timezone with tzinfo.

    Returns:
        datetime: Current datetime in local timezone with tzinfo.
    """

    _local_dt = datetime.now().astimezone()
    return _local_dt


@validate_arguments(config=dict(arbitrary_types_allowed=True))
def now_tz(tz: Union[ZoneInfo, tzinfo, str]) -> datetime:
    """Get current datetime in specified timezone with tzinfo.

    Args:
        tz (Union[ZoneInfo, tzinfo, str], required): Timezone info.

    Returns:
        datetime: Current datetime in specified timezone with tzinfo.
    """

    _dt = now_utc_tz()
    _dt = convert_tz(dt=_dt, tz=tz)
    return _dt


__all__ = [
    "add_tzinfo",
    "datetime_to_iso",
    "convert_tz",
    "now_utc_tz",
    "now_local_tz",
    "now_tz",
]
