# -*- coding: utf-8 -*-

import asyncio

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)

from src.config import config


## Async
def make_async_engine(dsn_url: str) -> AsyncEngine:
    """Create an async engine from a database connection string.

    Args:
        dsn_url (str, required): Database connection string as Data Source Name (URL).

    Returns:
        AsyncEngine: SQLAlchemy async engine for database.
    """

    _async_engine = create_async_engine(
        url=dsn_url,
        echo=config.db.echo_sql,
        echo_pool=config.db.echo_pool,
        pool_size=config.db.pool_size,
        pool_pre_ping=True,
        max_overflow=config.db.max_overflow,
        pool_recycle=config.db.pool_recycle,
        pool_timeout=config.db.pool_timeout,
    )

    return _async_engine


def create_async_session_maker(
    async_engine: AsyncEngine,
) -> async_scoped_session[AsyncSession]:
    """Create an async session maker from an async engine.

    Args:
        async_engine (AsyncEngine, required): SQLAlchemy async engine for session.

    Returns:
        async_scoped_session[AsyncSession]: SQLAlchemy async session maker.
    """

    _async_session_factory = async_sessionmaker(
        bind=async_engine, expire_on_commit=False
    )
    _AsyncSession = async_scoped_session(
        session_factory=_async_session_factory, scopefunc=asyncio.current_task
    )
    return _AsyncSession


## Sync
def make_engine(dsn_url: str) -> Engine:
    """Create an engine from a database connection string.

    Args:
        dsn_url (str, required): Database connection string as Data Source Name (URL).

    Returns:
        Engine: SQLAlchemy engine for database.
    """

    _engine = create_engine(
        url=dsn_url,
        echo=config.db.echo_sql,
        echo_pool=config.db.echo_pool,
        pool_size=config.db.pool_size,
        pool_pre_ping=True,
        max_overflow=config.db.max_overflow,
        pool_recycle=config.db.pool_recycle,
        pool_timeout=config.db.pool_timeout,
    )

    return _engine


def create_session_maker(engine: Engine) -> scoped_session[Session]:
    """Create a session maker from an engine.

    Args:
        engine (Engine, required): SQLAlchemy engine for session.

    Returns:
        scoped_session[Session]: SQLAlchemy session maker.
    """

    _session_factory = sessionmaker(bind=engine)
    _Session = scoped_session(session_factory=_session_factory)
    return _Session


__all__ = [
    "make_async_engine",
    "create_async_session_maker",
    "make_engine",
    "create_session_maker",
]
