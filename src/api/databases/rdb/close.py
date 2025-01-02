# -*- coding: utf-8 -*-

from typing import List, Union

from pydantic import validate_call
from sqlalchemy import Engine
from sqlalchemy.orm import scoped_session, close_all_sessions
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_scoped_session,
    close_all_sessions as async_close_all_sessions,
)

from api.logger import logger


## Async
@validate_call(config={"arbitrary_types_allowed": True})
async def async_close_db(
    sessions: List[Union[scoped_session, async_scoped_session]],
    engines: List[Union[Engine, AsyncEngine]],
) -> None:
    """Close all database sessions (connections) and dispose all engines.

    Args:
        sessions (List[Union[scoped_session, async_scoped_session]], required): List of SQLAlchemy sessions.
        engines  (List[Union[Engine, AsyncEngine]]                 , required): List of SQLAlchemy engines.
    """

    logger.info(f"Closing all database connections...")
    try:
        close_all_sessions()
        await async_close_all_sessions()
        # for _session in sessions:
        #     if isinstance(_session, scoped_session):
        #         # _session.remove()
        #         _session.close_all()
        #     elif isinstance(_session, async_scoped_session):
        #         # await _session.remove()
        #         await _session.close_all()

        for _engine in engines:
            if isinstance(_engine, Engine):
                _engine.dispose()
            elif isinstance(_engine, AsyncEngine):
                await _engine.dispose()

    except Exception:
        logger.exception("Failed to close database connections!")
        raise SystemExit(1)

    logger.success(f"Successfully closed all database connections.")


## Sync
@validate_call(config={"arbitrary_types_allowed": True})
def close_db(sessions: List[scoped_session], engines: List[Engine]) -> None:
    """Close all database sessions (connections) and dispose all engines.

    Args:
        sessions (List[scoped_session], required): List of SQLAlchemy sessions.
        engines  (List[Engine]        , required): List of SQLAlchemy engines.
    """

    logger.info(f"Closing all database connections...")
    try:
        # close_all_sessions()
        for _session in sessions:
            # _session.remove()
            _session.close_all()

        for _engine in engines:
            _engine.dispose()

    except Exception:
        logger.exception("Failed to close database connections!")
        raise SystemExit(1)

    logger.success(f"Successfully closed all database connections.")


__all__ = ["async_close_db", "close_db"]
