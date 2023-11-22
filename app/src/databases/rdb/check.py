# -*- coding: utf-8 -*-

import time
import asyncio

from sqlalchemy import Engine, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy_utils import database_exists, create_database
from fastapi.concurrency import run_in_threadpool

from src.config import config
from src.logger import logger


## Async
async def async_is_db_connectable(async_engine: AsyncEngine) -> bool:
    """Check if the database is connectable.

    Args:
        async_engine (AsyncEngine, required): SQLAlchemy async engine to check connection.

    Returns:
        bool: True if the database is connectable, False otherwise.
    """

    try:
        _url = async_engine.url
        if not database_exists(_url):
            logger.warning(f"'{_url.database}' database doesn't exist, creating...")
            await run_in_threadpool(create_database, url=_url)
            logger.success(f"Successfully created '{_url.database}' database.")

        async with async_engine.connect() as _connection:
            await _connection.execute(text("SELECT 1"))

        await async_engine.dispose()

        return True
    except Exception:
        return False


async def async_check_db(async_engine: AsyncEngine):
    """Check database connection, exit application if failed after few attempts.

    Args:
        async_engine (AsyncEngine, required): SQLAlchemy async engine to check connection.
    """

    _db_name = async_engine.url.database
    logger.info(f"Connecting to the '{_db_name}' database...")
    for _i in range(config.db.max_try_connect):
        logger.debug(f"Trying to connect '{_db_name}' database {_i + 1} time(s)...")

        if await async_is_db_connectable(async_engine=async_engine):
            break
        else:
            if (config.db.max_try_connect - 1) <= _i:
                logger.exception(
                    f"Falied to connect '{_db_name}' database {_i + 1} time(s)!"
                )
                exit(2)

            logger.debug(
                f"Failed to connect '{_db_name}' database {_i + 1} time(s), attempting to connect again after {config.db.wait_seconds_try_connect} second(s)..."
            )
            await asyncio.sleep(config.db.wait_seconds_try_connect)
    logger.success(f"Successfully connected to the '{_db_name}' database.")


## Sync
def is_db_connectable(engine: Engine) -> bool:
    """Check if the database is connectable.

    Args:
        engine (Engine, required): SQLAlchemy engine to check connection.

    Returns:
        bool: True if the database is connectable, False otherwise.
    """

    try:
        _url = engine.url
        if not database_exists(_url):
            logger.warning(f"'{_url.database}' database doesn't exist, creating...")
            create_database(_url)
            logger.success(f"Successfully created '{_url.database}' database.")

        with engine.connect() as _connection:
            _connection.execute(text("SELECT 1"))

        engine.dispose()

        return True
    except Exception:
        return False


def check_db(engine: Engine):
    """Check database connection, exit application if failed after few attempts.

    Args:
        engine (Engine, required): SQLAlchemy engine to check connection.
    """

    _db_name = engine.url.database
    logger.info(f"Connecting to the '{_db_name}' database...")
    for _i in range(config.db.max_try_connect):
        logger.debug(f"Trying to connect '{_db_name}' database {_i + 1} time(s)...")

        if is_db_connectable(engine=engine):
            break
        else:
            if (config.db.max_try_connect - 1) <= _i:
                logger.exception(
                    f"Falied to connect '{_db_name}' database {_i + 1} time(s)!"
                )
                exit(2)

            logger.debug(
                f"Failed to connect '{_db_name}' database {_i + 1} time(s), attempting to connect again after {config.db.wait_seconds_try_connect} second(s)..."
            )
            time.sleep(config.db.wait_seconds_try_connect)
    logger.success(f"Successfully connected to the '{_db_name}' database.")


__all__ = ["async_is_db_connectable", "async_check_db", "is_db_connectable", "check_db"]
