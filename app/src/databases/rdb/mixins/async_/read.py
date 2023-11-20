# -*- coding: utf-8 -*-

from typing import Union, List, Dict, Any

from sqlalchemy import Select, select, Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import DeclarativeBase, declarative_mixin
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import OrderDirect
from src.config import config
from src.logger import logger

from .basic import AsyncBasicMixin


@declarative_mixin
class AsyncReadMixin(AsyncBasicMixin):
    @classmethod
    async def async_select_by_where(
        cls,
        async_session: AsyncSession,
        where: Union[List[Dict[str, Any]], Dict[str, Any]],
        offset: int = 0,
        limit: int = config.db.select_limit,
        order_by: Union[List[str], str, None] = None,
        order_direct: OrderDirect = OrderDirect.DESC,
        disable_limit: bool = False,
        allow_no_result: bool = True,
    ) -> List[DeclarativeBase]:
        """Select ORM objects from database by where filter conditions.

        Args:
            async_session   (AsyncSession               , required): SQLAlchemy async_session for database connection.
            where           (Union[List[Dict[str, Any]],
                                         Dict[str, Any]], required): List of filter conditions.
            offset          (int                        , optional): Number of objects to skip. Defaults to 0.
            limit           (int                        , optional): Number of objects to limit. Defaults to `config.db.select_limit`.
            order_by        (Union[List[str], str, None], optional): List of order by columns. Defaults to None.
            order_direct    (OrderDirect                , optional): Sort order direction. Defaults to `OrderDirect.DESC`.
            disable_limit   (bool                       , optional): Disable select limit. Defaults to False.
            allow_no_result (bool                       , optional): Allow no result. Defaults to True.

        Raises:
            Exception    : If failed to get ORM objects from database by where filter conditions.
            NoResultFound: If no result found and `allow_no_result` is False.

        Returns:
            List[DeclarativeBase]: List of ORM objects.
        """

        _orm_objects: List[cls] = []
        try:
            _stmt: Select = cls._build_select(
                where=where,
                offset=offset,
                limit=limit,
                order_by=order_by,
                order_direct=order_direct,
                disable_limit=disable_limit,
            )

            _result: Result = await async_session.execute(_stmt)
            _orm_objects: List[cls] = _result.scalars().all()

        except Exception:
            logger.error(
                f"Failed to get '{cls.__name__}' objects from database by filtering with '{where}'!"
            )
            raise

        if (not allow_no_result) and (len(_orm_objects) == 0):
            raise NoResultFound(
                f"Not found any '{cls.__name__}' objects from database by filtering with '{where}'!"
            )

        return _orm_objects

    @classmethod
    async def async_select(
        cls,
        async_session: AsyncSession,
        offset: int = 0,
        limit: int = config.db.select_limit,
        allow_no_result: bool = True,
        disable_limit: bool = False,
    ) -> List[DeclarativeBase]:
        """Select ORM objects from database.

        Args:
            async_session   (AsyncSession, required): SQLAlchemy async_session for database connection.
            offset          (int         , optional): Number of objects to skip. Defaults to 0.
            limit           (int         , optional): Number of objects to limit. Defaults to <config.db.select_limit>.
            allow_no_result (bool        , optional): Allow no result. Defaults to True.
            disable_limit   (bool        , optional): Disable select limit. Defaults to False.

        Raises:
            NoResultFound: If no result found and `allow_no_result` is False.
            Exception    : If failed to get ORM objects from database.

        Returns:
            List[DeclarativeBase]: List of ORM objects.
        """

        _orm_objects: List[cls] = []
        try:
            _orm_objects: List[cls] = await cls.async_select_by_where(
                async_session=async_session,
                where=[],
                offset=offset,
                limit=limit,
                allow_no_result=allow_no_result,
                disable_limit=disable_limit,
            )
        except NoResultFound:
            raise
        except Exception:
            logger.error(f"Failed to get '{cls.__name__}' objects from database!")
            raise

        return _orm_objects

    @classmethod
    async def async_get(
        cls, async_session: AsyncSession, id: str, allow_no_result: bool = True
    ) -> Union[DeclarativeBase, None]:
        """Get ORM object from database by ID.

        Args:
            async_session   (AsyncSession, required): SQLAlchemy async_session for database connection.
            id              (str         , required): ID of object.
            allow_no_result (bool        , optional): Allow no result. Defaults to True.

        Raises:
            Exception    : If failed to get ORM object from database by ID.
            NoResultFound: If object ID doesn't exist in database and `allow_no_result` is False.

        Returns:
            Union[DeclarativeBase, None]: ORM object or None.
        """

        _orm_object: Union[cls, None] = None
        try:
            _orm_object: Union[cls, None] = await async_session.get(cls, id)
        except Exception:
            logger.error(
                f"Failed to get '{cls.__name__}' object with '{id}' ID from database!"
            )
            raise

        if (not allow_no_result) and (not _orm_object):
            raise NoResultFound(
                f"Not found any '{cls.__name__}' object with '{id}' ID from database!"
            )

        return _orm_object

    @classmethod
    async def async_get_by_where(
        cls,
        async_session: AsyncSession,
        where: Union[List[Dict[str, Any]], Dict[str, Any]],
        allow_no_result: bool = True,
    ) -> Union[DeclarativeBase, None]:
        """Get ORM object from database by where filter conditions.

        Args:
            async_session   (AsyncSession              , required): SQLAlchemy async_session for database connection.
            where           (Union[List[Dict[str, Any]],
                                        Dict[str, Any]], required): List of filter conditions. Defaults to None.
            allow_no_result (bool                      , optional): Allow no result. Defaults to True.

        Raises:
            NoResultFound: If object doesn't exist in database and `allow_no_result` is False.
            Exception    : If failed to get ORM object from database by where filter conditions.

        Returns:
            Union[DeclarativeBase, None]: ORM object or None.
        """

        _orm_object: Union[cls, None] = None
        try:
            _orm_objects: List[cls] = await cls.async_select_by_where(
                async_session=async_session,
                where=where,
                limit=1,
                allow_no_result=allow_no_result,
            )

            if 0 < len(_orm_objects):
                _orm_object: cls = _orm_objects[0]
        except NoResultFound:
            raise
        except Exception:
            logger.error(
                f"Failed to get '{cls.__name__}' object from database by '{where}' filter!"
            )
            raise

        return _orm_object

    @classmethod
    async def async_get_by_ids(
        cls,
        async_session: AsyncSession,
        ids: List[str],
    ) -> List[DeclarativeBase]:
        """Get ORM objects from database by IDs.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
            ids           (List[str]   , required): List of IDs.

        Raises:
            Exception: If failed to get ORM objects from database by IDs.

        Returns:
            List[DeclarativeBase]: List of ORM objects.
        """

        _orm_objects: List[cls] = []
        try:
            _stmt: Select = select(cls).where(cls.id.in_(ids))
            _result: Result = await async_session.execute(_stmt)
            _orm_objects: List[cls] = _result.scalars().all()
        except Exception:
            logger.error(
                f"Failed to get '{cls.__name__}' objects with '{ids}' IDs from database!"
            )
            raise

        return _orm_objects


__all__ = ["AsyncReadMixin"]
