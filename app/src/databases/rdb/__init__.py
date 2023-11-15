# -*- coding: utf-8 -*-

from src.config import config
from .connect import *
from .check import *
from .load import *
from .close import *


register_models()

## Async
write_async_engine = make_async_engine(dsn_url=config.db.dsn_url)
WriteAsyncSession = create_async_session_maker(async_engine=write_async_engine)

read_async_engine = make_async_engine(dsn_url=config.db.read_dsn_url)
ReadAsyncSession = create_async_session_maker(async_engine=read_async_engine)

## Sync
write_engine = make_engine(dsn_url=config.db.dsn_url)
WriteSession = create_session_maker(engine=write_engine)

read_engine = make_engine(dsn_url=config.db.read_dsn_url)
ReadSession = create_session_maker(engine=read_engine)


engines = [
    write_async_engine,
    read_async_engine,
    write_engine,
    read_engine,
]
sessions = [
    WriteAsyncSession,
    ReadAsyncSession,
    WriteSession,
    ReadSession,
]


__all__ = [
    "write_async_engine",
    "read_async_engine",
    "WriteAsyncSession",
    "ReadAsyncSession",
    "write_engine",
    "WriteSession",
    "read_engine",
    "ReadSession",
    "engines",
    "sessions",
    "make_async_engine",
    "create_async_session_maker",
    "async_is_db_connectable",
    "async_check_db",
    "async_load_structure",
    "async_close_db",
    "make_engine",
    "create_session_maker",
    "is_db_connectable",
    "check_db",
    "load_structure",
    "close_db",
]
