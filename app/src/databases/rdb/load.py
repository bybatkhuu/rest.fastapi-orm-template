# -*- coding: utf-8 -*-

from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.models import BaseORM
from src.logger import logger


def register_models():
    # Add all your models here...
    from src.resources.task.models import TaskORM


## Async
async def async_load_structure(async_engine: AsyncEngine):
    """Initialize and syncronize database structure.

    Args:
        async_engine (AsyncEngine, required): SQLAlchemy async engine to initialize database structure.
    """

    _db_name = async_engine.url.database
    logger.info(f"Initializing '{_db_name}' database structure...")
    try:
        async with async_engine.begin() as _connection:
            register_models()
            await _connection.run_sync(BaseORM.metadata.create_all)

    except Exception:
        await async_engine.dispose()
        logger.exception(f"Failed to create '{_db_name}' database structure!")
        raise
        # exit(2)
    finally:
        await async_engine.dispose()
    logger.success(f"Successfully initialized '{_db_name}' database structure.")


## Sync
def load_structure(engine: Engine):
    """Initialize and syncronize database structure.

    Args:
        engine (Engine, required): SQLAlchemy engine to initialize database structure.
    """

    _db_name = engine.url.database
    logger.info(f"Initializing '{_db_name}' database structure...")
    try:
        with engine.begin() as _connection:
            register_models()
            BaseORM.metadata.create_all(bind=_connection)

    except Exception:
        engine.dispose()
        logger.exception(f"Failed to create '{_db_name}' database structure!")
        raise
        # exit(2)
    finally:
        engine.dispose()
    logger.success(f"Successfully initialized '{_db_name}' database structure.")


__all__ = ["register_models", "async_load_structure", "load_structure"]
