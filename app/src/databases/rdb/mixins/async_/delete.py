# -*- coding: utf-8 -*-

from typing import List, Dict, Union, Any

from sqlalchemy import Delete, delete, Result
from sqlalchemy.orm import DeclarativeBase, declarative_mixin
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger

from .read import AsyncReadMixin


@declarative_mixin
class AsyncDeleteMixin(AsyncReadMixin):
    async def async_delete(self, async_session: AsyncSession, auto_commit: bool = True):
        """Delete ORM object from database.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.

        Raises:
            Exception: If failed to delete ORM object from database.
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
        cls,
        async_session: AsyncSession,
        id: str,
        orm_way: bool = False,
        auto_commit: bool = True,
    ):
        """Delete ORM object from database by ID.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
            id            (str         , required): ORM object ID.
            auto_commit   (bool        , optional): Auto commit. Defaults to True.

        Raises:
            NoResultFound: If ORM object ID not found in database, when `orm_way` is True.
            Exception    : If failed to delete ORM object from database by ID.
        """

        try:
            if orm_way:
                _orm_object: cls = await cls.async_get(
                    async_session=async_session, id=id, allow_no_result=False
                )
                await _orm_object.async_delete(
                    async_session=async_session, auto_commit=auto_commit
                )
            else:
                _stmt: Delete = delete(cls).where(cls.id == id)
                _result: Result = await async_session.execute(_stmt)

                if auto_commit:
                    await async_session.commit()

                logger.debug(
                    f"Deleted '{_result.rowcount}' row(s) from '{cls.__name__}' table."
                )

                if _result.rowcount == 0:
                    raise NoResultFound(
                        f"Not found any '{cls.__name__}' object with '{id}' ID from database!"
                    )
        except NoResultFound:
            if (not orm_way) and auto_commit:
                await async_session.rollback()

            raise
        except Exception:
            if (not orm_way) and auto_commit:
                await async_session.rollback()

            logger.error(
                f"Failed to delete '{cls.__name__}' object '{id}' ID from database!"
            )
            raise

    @classmethod
    async def async_delete_by_ids(
        cls, async_session: AsyncSession, ids: List[str], auto_commit: bool = True
    ):
        """Delete rows/ORM objects from database by ID list.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
            ids           (List[str]   , required): List of IDs.
            auto_commit   (bool        , optional): Auto commit. Defaults to True.

        Raises:
            Exception: If failed to delete rows/ORM objects from database.
        """

        if 0 < len(ids):
            try:
                _stmt: Delete = delete(cls).where(cls.id.in_(ids))
                _result: Result = await async_session.execute(_stmt)

                if auto_commit:
                    await async_session.commit()

                logger.debug(
                    f"Deleted '{_result.rowcount}' row(s) from '{cls.__name__}' table."
                )
            except Exception:
                if auto_commit:
                    await async_session.rollback()

                logger.error(
                    f"Failed to delete '{cls.__name__}' objects by ID list from database!"
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

        Raises:
            Exception: If failed to delete ORM objects from database.
        """

        if 0 < len(orm_objects):
            try:
                for _orm_object in orm_objects:
                    await async_session.delete(_orm_object)

                if auto_commit:
                    await async_session.commit()
            except Exception:
                if auto_commit:
                    await async_session.rollback()

                logger.error(
                    f"Failed to delete '{cls.__name__}' objects from database!"
                )
                raise

    @classmethod
    async def async_delete_by_where(
        cls,
        async_session: AsyncSession,
        where: Union[List[Dict[str, Any]], Dict[str, Any]],
        orm_way: bool = False,
        auto_commit: bool = True,
    ):
        """Delete ORM objects from database by filter conditions.

        Args:
            async_session (AsyncSession              , required): SQLAlchemy async_session for database connection.
            where         (Union[List[Dict[str, Any]],
                                      Dict[str, Any]], required): List of filter conditions.
            orm_way       (bool                      , optional): Use ORM way to delete objects. Defaults to False.
            auto_commit   (bool                      , optional): Auto commit. Defaults to True.

        Raises:
            Exception: If failed to delete ORM objects from database by filter conditions.
        """

        try:
            if orm_way:
                _orm_objects: List[cls] = await cls.async_select_by_where(
                    async_session=async_session, where=where, disable_limit=True
                )

                if 0 < len(_orm_objects):
                    await cls.async_delete_objects(
                        async_session=async_session,
                        orm_objects=_orm_objects,
                        auto_commit=auto_commit,
                    )
            else:
                _stmt: Delete = delete(cls)
                _stmt = cls._build_where_stmt(stmt=_stmt, where=where)
                _result: Result = await async_session.execute(_stmt)

                if auto_commit:
                    await async_session.commit()

                logger.debug(
                    f"Deleted '{_result.rowcount}' row(s) from '{cls.__name__}' table."
                )
        except Exception:
            if (not orm_way) and auto_commit:
                await async_session.rollback()

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

        Raises:
            Exception: If failed to delete all ORM objects from database.
        """

        try:
            _stmt = delete(cls)
            _result: Result = await async_session.execute(_stmt)

            if auto_commit:
                await async_session.commit()

            logger.debug(
                f"Deleted '{_result.rowcount}' row(s) from '{cls.__name__}' table."
            )
        except Exception:
            if auto_commit:
                await async_session.rollback()

            logger.error(
                f"Failed to delete all '{cls.__name__}' objects from database!"
            )
            raise


__all__ = ["AsyncDeleteMixin"]
