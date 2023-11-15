# -*- coding: utf-8 -*-

from sqlalchemy.orm import DeclarativeBase, declarative_mixin
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger

from .base import BaseMixin


@declarative_mixin
class CreateMixin(BaseMixin):
    @classmethod
    async def async_insert(
        cls, async_session: AsyncSession, auto_commit: bool = True, **kwargs
    ) -> DeclarativeBase:
        """Create and save new ORM object into database.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
            auto_commit   (bool        , optional): Auto commit. Defaults to True.
            **kwargs      (dict        , required): Dictionary of object data.

        Raises:
            IntegrityError: If object with same ID already exists in database.

        Returns:
            DeclarativeBase: New ORM object.
        """

        if "id" not in kwargs:
            kwargs["id"] = cls.create_unique_id()

        _orm_object = cls(**kwargs)
        try:
            async_session.add(_orm_object)
            if auto_commit:
                await async_session.commit()
                await async_session.refresh(_orm_object)
        except IntegrityError:
            logger.warning(
                f"'{cls.__name__}' '{kwargs['id']}' ID already exists in database!"
            )
            raise
        except Exception:
            if auto_commit:
                await async_session.rollback()
            logger.error(
                f"Failed to save '{cls.__name__}' object '{kwargs['id']}' ID into database!"
            )
            raise

        return _orm_object


__all__ = ["CreateMixin"]
