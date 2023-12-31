# -*- coding: utf-8 -*-

# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.databases.rdb import (
    AsyncWriteSession,
    AsyncReadSession,
    # WriteSession,
    # ReadSession,
)


async def async_get_write_db() -> AsyncSession:
    """Get write async database session.

    Returns:
        AsyncSession: SQLAlchemy async session.

    Yields:
        Iterator[AsyncSession]: SQLAlchemy async session.
    """

    async with AsyncWriteSession() as _async_write_session:
        yield _async_write_session


async def async_get_read_db() -> AsyncSession:
    """Get read async database session.

    Returns:
        AsyncSession: SQLAlchemy async session.

    Yields:
        Iterator[AsyncSession]: SQLAlchemy async session.
    """

    async with AsyncReadSession() as _async_read_session:
        yield _async_read_session


# def get_write_db() -> Session:
#     """Get write database session.

#     Returns:
#         Session: SQLAlchemy session.

#     Yields:
#         Iterator[Session]: SQLAlchemy session.
#     """

#     with WriteSession() as _write_session:
#         yield _write_session


# def get_read_db() -> Session:
#     """Get read database session.

#     Returns:
#         Session: SQLAlchemy session.

#     Yields:
#         Iterator[Session]: SQLAlchemy session.
#     """

#     with ReadSession() as _read_session:
#         yield _read_session


__all__ = [
    "async_get_write_db",
    "async_get_read_db",
    # "get_write_db",
    # "get_read_db",
]
