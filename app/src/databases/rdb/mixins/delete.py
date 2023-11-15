# -*- coding: utf-8 -*-

from typing import List, Dict, Union, Any

from sqlalchemy import delete
from sqlalchemy.orm import DeclarativeBase, declarative_mixin
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger

from .read import ReadMixin


@declarative_mixin
class DeleteMixin(ReadMixin):
    async def async_delete(self, async_session: AsyncSession, auto_commit: bool = True):
        """Delete ORM object from database.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
        """

        try:
            await async_session.delete(self)
            if auto_commit:
                await async_session.commit()
        except Exception:
            if auto_commit:
                await async_session.rollback()
            logger.error(
                f"Failed to delete '{self.__class__.__name__}' object '{self.id}' ID from database!"
            )
            raise

    @classmethod
    async def async_delete_by_id(
        cls, async_session: AsyncSession, id: str, auto_commit: bool = True
    ):
        """Delete ORM object from database by ID.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
            id            (str         , required): ORM object ID.
            auto_commit   (bool        , optional): Auto commit. Defaults to True.

        Raises:
            NoResultFound: Raise error if ORM object ID not found in database.
        """

        try:
            _orm_object: cls = await cls.async_get(
                async_session=async_session, id=id, allow_no_result=False
            )
            await _orm_object.async_delete(
                async_session=async_session, auto_commit=auto_commit
            )
        except NoResultFound:
            raise
        except Exception:
            logger.error(
                f"Failed to delete '{cls.__name__}' object '{id}' ID from database!"
            )
            raise

    @classmethod
    async def async_delete_objects(
        cls,
        async_session: AsyncSession,
        orm_objects: List[DeclarativeBase],
        auto_commit: bool = True,
    ):
        """Delete ORM objects from database.

        Args:
            async_session (AsyncSession         , required): SQLAlchemy
            objects       (List[DeclarativeBase], required): List of ORM objects.
            auto_commit   (bool                 , optional): Auto commit. Defaults to True.
        """

        try:
            if 0 < len(orm_objects):
                for _orm_object in orm_objects:
                    await async_session.delete(_orm_object)

                if auto_commit:
                    await async_session.commit()
        except Exception:
            if auto_commit:
                await async_session.rollback()
            logger.error(f"Failed to delete '{cls.__name__}' objects from database!")
            raise

    @classmethod
    async def async_delete_by_where(
        cls,
        async_session: AsyncSession,
        where: Union[List[Dict[str, Any]], Dict[str, Any]],
        auto_commit: bool = True,
    ):
        """Delete ORM objects from database by filter conditions.

        Args:
            async_session (AsyncSession              , required): SQLAlchemy async_session for database connection.
            where         (Union[List[Dict[str, Any]],
                                      Dict[str, Any]], required): List of filter conditions.
            auto_commit   (bool                      , optional): Auto commit. Defaults to True.
        """

        try:
            _orm_objects: List[cls] = await cls.async_select_by_where(
                async_session=async_session, where=where, disable_limit=True
            )

            if 0 < len(_orm_objects):
                await cls.async_delete_objects(
                    async_session=async_session,
                    orm_objects=_orm_objects,
                    auto_commit=auto_commit,
                )
        except Exception:
            logger.error(
                f"Failed to delete '{cls.__name__}' object by '{where}' filter from database!"
            )
            raise

    @classmethod
    async def async_delete_all(
        cls, async_session: AsyncSession, auto_commit: bool = True
    ):
        """Delete all ORM objects from database.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
            auto_commit   (bool        , optional): Auto commit. Defaults to True.
        """

        try:
            # _stmt = cls.__table__.delete()
            _stmt = delete(cls)
            await async_session.execute(_stmt)
            if auto_commit:
                await async_session.commit()
        except Exception:
            if auto_commit:
                await async_session.rollback()
            logger.error(
                f"Failed to delete all '{cls.__name__}' objects from database!"
            )
            raise


__all__ = ["DeleteMixin"]
