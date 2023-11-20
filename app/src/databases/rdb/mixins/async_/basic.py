# -*- coding: utf-8 -*-

from typing import Union, List, Dict, Any

from sqlalchemy import func, Select, select, Result
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger
from src.databases.rdb.mixins.base import BaseMixin


@declarative_mixin
class AsyncBasicMixin(BaseMixin):
    @classmethod
    async def async_exists_by_id(cls, async_session: AsyncSession, id: str) -> bool:
        """Check if ORM object exists in database by ID.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
            id            (str         , required): ID of object.

        Raises:
            Exception: If failed to check if ORM object exists in database by ID.

        Returns:
            bool: True if exists, False otherwise.
        """

        _is_exists = False
        try:
            _stmt: Select = select(cls.id).where(cls.id == id)
            _result: Result = await async_session.execute(_stmt)
            if _result.scalar():
                _is_exists = True
        except Exception:
            logger.error(
                f"Failed to check if '{cls.__name__}' object '{id}' ID exists in database!"
            )
            raise

        return _is_exists

    async def async_exists(self, async_session: AsyncSession) -> bool:
        """Check if ORM object exists in database.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.

        Raises:
            Exception: If failed to check if ORM object exists in database.

        Returns:
            bool: True if exists, False otherwise.
        """

        _is_exists = False
        try:
            _is_exists = await self.__class__.async_exists_by_id(
                async_session=async_session, id=self.id
            )
        except Exception:
            logger.error(
                f"Failed to check if '{self.__class__.__name__}' object '{self.id}' ID exists in database!"
            )
            raise

        return _is_exists

    @classmethod
    async def async_count_by_where(
        cls,
        async_session: AsyncSession,
        where: Union[List[Dict[str, Any]], Dict[str, Any]],
    ) -> int:
        """Count ORM objects in database by filter conditions.

        Args:
            async_session (AsyncSession              , required): SQLAlchemy async_session for database connection.
            where         (Union[List[Dict[str, Any]],
                                      Dict[str, Any]], required): List of filter conditions.

        Raises:
            Exception: If failed to count ORM objects in database by filter conditions.

        Returns:
            int: Count of ORM objects in database.
        """

        _count = 0
        try:
            _stmt: Select = select(func.count()).select_from(cls)
            if where:
                _stmt: Select = cls._build_where(stmt=_stmt, where=where)

            _result: Result = await async_session.execute(_stmt)
            _count: int = _result.scalar()
        except Exception:
            logger.error(
                f"Failed to count '{cls.__name__}' objects by '{where}' filter in database!"
            )
            raise

        return _count

    @classmethod
    async def async_count(cls, async_session: AsyncSession) -> int:
        """Count all ORM objects in database.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.

        Raises:
            Exception: If failed to count ORM objects in database.

        Returns:
            int: Count of ORM objects in database.
        """

        _count = 0
        try:
            _count: int = await cls.async_count_by_where(
                async_session=async_session, where=[]
            )
        except Exception:
            logger.error(f"Failed to count '{cls.__name__}' objects from database!")
            raise

        return _count


__all__ = ["AsyncBasicMixin"]
