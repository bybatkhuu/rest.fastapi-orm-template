# -*- coding: utf-8 -*-

import time
import asyncio

from sqlalchemy import Engine, text, URL, Result
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy_utils import database_exists, create_database
from fastapi.concurrency import run_in_threadpool

from src.core.constants import WarnEnum
from src.config import config
from src.logger import logger


## Async
async def async_create_db(
    async_engine: AsyncEngine, warn_mode: WarnEnum = WarnEnum.ERROR
) -> bool:
    """Create database if it doesn't exist.

    Args:
        async_engine (AsyncEngine, required): SQLAlchemy async engine to create database.
        warn_mode    (WarnEnum   , optional): Warning mode. Defaults to WarnEnum.ERROR.

    Raises:
        Exception: If can't create/connect database and `warn_mode` is set to WarnEnum.ERROR.

    Returns:
        bool: True if the database exists, False otherwise.
    """

    _is_db_exists = False
    try:
        _url: URL = async_engine.url
        if not await run_in_threadpool(database_exists, url=_url):
            logger.warning(
                f"Can't connect to '{_url.database}' database or doesn't exist, trying to create it..."
            )
            await run_in_threadpool(create_database, url=_url)
            logger.success(f"Successfully created '{_url.database}' database.")

        _is_db_exists = True
    except Exception:
        _message = f"Failed to create '{_url.database}' database!"
        if warn_mode == WarnEnum.ALWAYS:
            logger.error(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)
        elif warn_mode == WarnEnum.ERROR:
            raise

    return _is_db_exists


async def async_is_db_connectable(async_engine: AsyncEngine) -> bool:
    """Check if the database is connectable.

    Args:
        async_engine (AsyncEngine, required): SQLAlchemy async engine to check connection.

    Returns:
        bool: True if the database is connectable, False otherwise.
    """

    _is_connectable = False
    try:
        async with async_engine.connect() as _connection:
            _result: Result = await _connection.execute(text("SELECT 1"))
            _is_connectable = bool(_result.scalar())
    except Exception:
        pass
    finally:
        await async_engine.dispose()

    return _is_connectable


async def async_check_db(async_engine: AsyncEngine, is_write_db: bool = True) -> bool:
    """Check database connection, exit application if failed after few attempts.

    Args:
        async_engine (AsyncEngine, required): SQLAlchemy async engine to check connection.
        is_write_db  (bool       , optional): If True, create database if it doesn't exist. Defaults to True.

    Raises:
        ConnectionError: If can't connect to database after few attempts.

    Returns:
        bool: True if the database is exists and connectable, False otherwise.
    """

    _is_done = False
    _tmp_str = "" if is_write_db else "read "
    _db_name = async_engine.url.database
    logger.info(f"Connecting to the '{_db_name}' {_tmp_str}database...")
    for _i in range(config.db.max_try_connect):
        # logger.debug(f"Trying to connect '{_db_name}' {_tmp_str}database {_i + 1} time(s)...")

        if is_write_db:
            await async_create_db(async_engine=async_engine, warn_mode=WarnEnum.IGNORE)

        if await async_is_db_connectable(async_engine=async_engine):
            _is_done = True
            break
        else:
            if (config.db.max_try_connect - 1) <= _i:
                _message = f"Falied to connect '{_db_name}' {_tmp_str}database {_i + 1} time(s)!"
                logger.error(_message)
                raise ConnectionError(_message)
                # exit(2)

            logger.warning(
                f"Unable to connect '{_db_name}' {_tmp_str}database {_i + 1} time(s), retrying in {config.db.wait_seconds_try_connect} second(s)..."
            )
            await asyncio.sleep(config.db.wait_seconds_try_connect)

    logger.success(f"Successfully connected to the '{_db_name}' {_tmp_str}database.")
    return _is_done


## Sync
def create_db(engine: Engine, warn_mode: WarnEnum = WarnEnum.ERROR) -> bool:
    """Create database if it doesn't exist.

    Args:
        engine    (Engine  , required): SQLAlchemy engine to create database.
        warn_mode (WarnEnum, optional): Warning mode. Defaults to WarnEnum.ERROR.

    Raises:
        Exception: If can't create/connect database and `warn_mode` is set to WarnEnum.ERROR.

    Returns:
        bool: True if the database exists, False otherwise.
    """

    _is_db_exists = False
    try:
        _url: URL = engine.url
        if not database_exists(url=_url):
            logger.warning(
                f"Can't connect to '{_url.database}' database or doesn't exist, trying to create it..."
            )
            create_database(url=_url)
            logger.success(f"Successfully created '{_url.database}' database.")

        _is_db_exists = True
    except Exception:
        _message = f"Failed to create '{_url.database}' database!"
        if warn_mode == WarnEnum.ALWAYS:
            logger.error(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)
        elif warn_mode == WarnEnum.ERROR:
            raise

    return _is_db_exists


def is_db_connectable(engine: Engine) -> bool:
    """Check if the database is connectable.

    Args:
        engine (Engine, required): SQLAlchemy engine to check connection.

    Returns:
        bool: True if the database is connectable, False otherwise.
    """

    _is_connectable = False
    try:
        with engine.connect() as _connection:
            _result: Result = _connection.execute(text("SELECT 1"))
            _is_connectable = bool(_result.scalar())
    except Exception:
        pass
    finally:
        engine.dispose()

    return _is_connectable


def check_db(engine: Engine, is_write_db: bool = True) -> bool:
    """Check database connection, exit application if failed after few attempts.

    Args:
        engine       (Engine, required): SQLAlchemy engine to check connection.
        is_write_db  (bool  , optional): If True, create database if it doesn't exist. Defaults to True.

    Raises:
        ConnectionError: If can't connect to database after few attempts.

    Returns:
        bool: True if the database is exists and connectable, False otherwise.
    """

    _is_done = False
    _tmp_str = "" if is_write_db else "read "
    _db_name = engine.url.database
    logger.info(f"Connecting to the '{_db_name}' {_tmp_str}database...")
    for _i in range(config.db.max_try_connect):
        # logger.debug(f"Trying to connect '{_db_name}' {_tmp_str}database {_i + 1} time(s)...")

        if is_write_db:
            create_db(engine=engine, warn_mode=WarnEnum.IGNORE)

        if is_db_connectable(engine=engine):
            _is_done = True
            break
        else:
            if (config.db.max_try_connect - 1) <= _i:
                _message = f"Falied to connect '{_db_name}' {_tmp_str}database {_i + 1} time(s)!"
                logger.error(_message)
                raise ConnectionError(_message)
                # exit(2)

            logger.warning(
                f"Unable to connect '{_db_name}' {_tmp_str}database {_i + 1} time(s), retrying in {config.db.wait_seconds_try_connect} second(s)..."
            )
            time.sleep(config.db.wait_seconds_try_connect)

    logger.success(f"Successfully connected to the '{_db_name}' {_tmp_str}database.")
    return _is_done


__all__ = [
    "async_create_db",
    "async_is_db_connectable",
    "async_check_db",
    "create_db",
    "is_db_connectable",
    "check_db",
]
