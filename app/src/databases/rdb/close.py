# -*- coding: utf-8 -*-

from typing import List, Union

from sqlalchemy import Engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.asyncio import AsyncEngine, async_scoped_session

from src.logger import logger


## Async
async def async_close_db(
    sessions: List[Union[scoped_session, async_scoped_session]],
    engines: List[Union[Engine, AsyncEngine]],
):
    """Close all database sessions (connections) and dispose all engines.

    Args:
        sessions (List[Union[scoped_session, async_scoped_session]], required): List of SQLAlchemy sessions.
        engines  (List[Union[Engine, AsyncEngine]]                 , required): List of SQLAlchemy engines.
    """

    logger.info(f"Closing all database connections...")
    try:
        for _session in sessions:
            if isinstance(_session, scoped_session):
                _session.remove()
            elif isinstance(_session, async_scoped_session):
                await _session.remove()

        for _engine in engines:
            if isinstance(_engine, Engine):
                _engine.dispose()
            elif isinstance(_engine, AsyncEngine):
                await _engine.dispose()

    except Exception:
        logger.exception("Failed to close database connections!")
        exit(2)
    logger.success(f"Successfully closed all database connections.")


## Sync
def close_db(sessions: List[scoped_session], engines: List[Engine]):
    """Close all database sessions (connections) and dispose all engines.

    Args:
        sessions (List[scoped_session], required): List of SQLAlchemy sessions.
        engines  (List[Engine]        , required): List of SQLAlchemy engines.
    """

    logger.info(f"Closing all database connections...")
    try:
        for _session in sessions:
            _session.remove()

        for _engine in engines:
            _engine.dispose()

    except Exception:
        logger.exception("Failed to close database connections!")
        exit(2)
    logger.success(f"Successfully closed all database connections.")


__all__ = ["async_close_db", "close_db"]
