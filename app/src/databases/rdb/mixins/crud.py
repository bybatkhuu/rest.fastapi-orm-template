# -*- coding: utf-8 -*-

from typing import Union

from sqlalchemy.orm import DeclarativeBase, declarative_mixin, Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger

from .read import ReadMixin
from .create import CreateMixin
from .update import UpdateMixin
from .delete import DeleteMixin


@declarative_mixin
class CRUDMixin(DeleteMixin, UpdateMixin, CreateMixin, ReadMixin):
    ## Async methods
    @classmethod
    async def async_save(
        cls, async_session: AsyncSession, auto_commit: bool = True, **kwargs
    ) -> DeclarativeBase:
        """Save ORM object into database.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
            auto_commit   (bool        , optional): Auto commit. Defaults to True.
            **kwargs      (dict        , required): Dictionary of ORM object data.

        Returns:
            DeclarativeBase: Created or updated ORM object.
        """

        _orm_object: Union[cls, None] = None
        try:
            _is_updated = False
            if "id" in kwargs:
                _orm_object = await cls.async_get(
                    async_session=async_session, id=kwargs["id"]
                )

                if _orm_object:
                    kwargs.pop("id")
                    _is_updated = True
                    _orm_object = await _orm_object.async_update(
                        async_session=async_session, auto_commit=auto_commit, **kwargs
                    )

            if not _is_updated:
                _orm_object = await cls.async_insert(
                    async_session=async_session, auto_commit=auto_commit, **kwargs
                )

        except Exception:
            logger.error(f"Failed to save '{cls.__name__}' object into database!")
            raise

        return _orm_object

    ## Sync methods
    @classmethod
    def save(
        cls, session: Session, auto_commit: bool = True, **kwargs
    ) -> DeclarativeBase:
        """Save ORM object into database.

        Args:
            session     (Session, required): SQLAlchemy session for database connection.
            auto_commit (bool   , optional): Auto commit. Defaults to True.
            **kwargs    (dict   , required): Dictionary of ORM object data.

        Returns:
            DeclarativeBase: Created or updated ORM object.
        """

        _orm_object: Union[cls, None] = None
        try:
            _is_updated = False
            if "id" in kwargs:
                _orm_object = cls.get(session=session, id=kwargs["id"])

                if _orm_object:
                    kwargs.pop("id")
                    _is_updated = True
                    _orm_object = _orm_object.update(
                        session=session, auto_commit=auto_commit, **kwargs
                    )

            if not _is_updated:
                _orm_object = cls.insert(
                    session=session, auto_commit=auto_commit, **kwargs
                )

        except Exception:
            logger.error(f"Failed to save '{cls.__name__}' object into database!")
            raise

        return _orm_object


__all__ = ["CRUDMixin"]
