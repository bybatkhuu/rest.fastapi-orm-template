# -*- coding: utf-8 -*-

from typing import Union, List, Dict, Any

from sqlalchemy import Select, select, desc, asc, ChunkedIteratorResult, Subquery
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import DeclarativeBase, declarative_mixin, Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import OrderDirect
from src.config import config
from src.logger import logger

from .base import BaseMixin


@declarative_mixin
class ReadMixin(BaseMixin):
    @classmethod
    def _build_select(
        cls,
        where: Union[List[Dict[str, Any]], Dict[str, Any], None] = None,
        offset: int = 0,
        limit: int = config.db.select_limit,
        order_by: Union[List[str], str, None] = None,
        order_direct: OrderDirect = OrderDirect.DESC,
        disable_limit: bool = False,
    ) -> Select:
        """Build SQLAlchemy select statement for ORM object.

        Args:
            where         (Union[List[Dict[str, Any]],
                                 Dict[str, Any], None], optional): List of filter conditions. Defaults to None.
            offset        (int                        , optional): Offset number. Defaults to 0.
            limit         (int                        , optional): Limit number. Defaults to `config.db.select_limit`.
            order_by      (Union[List[str], str, None], optional): List of order by columns. Defaults to None.
            order_direct  (OrderDirect                , optional): Sort order direction. Defaults to `OrderDirect.DESC`.
            disable_limit (bool                       , optional): Disable select limit. Defaults to False.

        Returns:
            Select: Built SQLAlchemy select statement.
        """

        _order_direct = desc
        if order_direct == OrderDirect.ASC:
            _order_direct = asc

        ## Deffered join to improve performance:
        # Subquery:
        _sub_query: Select = select(cls.id)
        if where:
            _sub_query = cls._build_where(stmt=_sub_query, where=where)

        if order_by:
            if isinstance(order_by, str):
                order_by = [order_by]

            if isinstance(order_by, list):
                for _order_by in order_by:
                    _sub_query = _sub_query.order_by(
                        _order_direct(getattr(cls, _order_by))
                    )

        _sub_query: Select = _sub_query.order_by(_order_direct(cls.id))

        if not disable_limit:
            _sub_query = _sub_query.limit(limit).offset(offset)
        # Make into subquery:
        _sub_query: Subquery = _sub_query.subquery()

        # Main query:
        _stmt: Select = select(cls).join(_sub_query, cls.id == _sub_query.c.id)
        if order_by:
            if isinstance(order_by, str):
                order_by = [order_by]

            if isinstance(order_by, list):
                for _order_by in order_by:
                    _stmt = _stmt.order_by(_order_direct(getattr(cls, _order_by)))

        _stmt = _stmt.order_by(_order_direct(cls.id))

        return _stmt

    ## Async:
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

            # Execute query:
            _result: ChunkedIteratorResult = await async_session.execute(_stmt)
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
            NoResultFound: If object ID doesn't exist in database and `allow_no_result` is False.

        Returns:
            Union[DeclarativeBase, None]: ORM object or None.
        """

        _orm_object: Union[cls, None] = None
        try:
            _orm_object: Union[cls, None] = await async_session.get(cls, id)
        except Exception:
            logger.error(
                f"Failed to get '{cls.__name__}' object '{id}' ID from database!"
            )
            raise

        if (not allow_no_result) and (not _orm_object):
            raise NoResultFound(
                f"Not found '{cls.__name__}' any object '{id}' ID from database!"
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

    ## Sync:
    @classmethod
    def select_by_where(
        cls,
        session: Session,
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
            session         (Session                    , required): SQLAlchemy session for database connection.
            where           (Union[List[Dict[str, Any]],
                                         Dict[str, Any]], required): List of filter conditions.
            offset          (int                        , optional): Number of objects to skip. Defaults to 0.
            limit           (int                        , optional): Number of objects to limit. Defaults to `config.db.select_limit`.
            order_by        (Union[List[str], str, None], optional): List of order by columns. Defaults to None.
            order_direct    (OrderDirect                , optional): Sort order direction. Defaults to `OrderDirect.DESC`.
            disable_limit   (bool                       , optional): Disable select limit. Defaults to False.
            allow_no_result (bool                       , optional): Allow no result. Defaults to True.

        Raises:
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

            # Execute query:
            _result: ChunkedIteratorResult = session.execute(_stmt)
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
    def select(
        cls,
        session: Session,
        offset: int = 0,
        limit: int = config.db.select_limit,
        allow_no_result: bool = True,
        disable_limit: bool = False,
    ) -> List[DeclarativeBase]:
        """Select ORM objects from database.

        Args:
            session   (Session, required): SQLAlchemy session for database connection.
            offset          (int         , optional): Number of objects to skip. Defaults to 0.
            limit           (int         , optional): Number of objects to limit. Defaults to `config.db.select_limit`.
            allow_no_result (bool        , optional): Allow no result. Defaults to True.
            disable_limit   (bool        , optional): Disable select limit. Defaults to False.

        Raises:
            NoResultFound: If no result found and `allow_no_result` is False.

        Returns:
            List[DeclarativeBase]: List of ORM objects.
        """

        _orm_objects: List[cls] = []
        try:
            _orm_objects: List[cls] = cls.select_by_where(
                session=session,
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
    def get(
        cls, session: Session, id: str, allow_no_result: bool = True
    ) -> Union[DeclarativeBase, None]:
        """Get ORM object from database by ID.

        Args:
            session         (Session, required): SQLAlchemy session for database connection.
            id              (str    , required): ID of object.
            allow_no_result (bool   , optional): Allow no result. Defaults to True.

        Raises:
            NoResultFound: If object ID doesn't exist in database and `allow_no_result` is False.

        Returns:
            Union[DeclarativeBase, None]: ORM object or None.
        """

        _orm_object: Union[cls, None] = None
        try:
            _orm_object: Union[cls, None] = session.get(cls, id)
        except Exception:
            logger.error(
                f"Failed to get '{cls.__name__}' object '{id}' ID from database!"
            )
            raise

        if (not allow_no_result) and (not _orm_object):
            raise NoResultFound(
                f"Not found '{cls.__name__}' any object '{id}' ID from database!"
            )

        return _orm_object

    @classmethod
    def get_by_where(
        cls,
        session: Session,
        where: Union[List[Dict[str, Any]], Dict[str, Any]],
        allow_no_result: bool = True,
    ) -> Union[DeclarativeBase, None]:
        """Get ORM object from database by where filter conditions.

        Args:
            session         (Session                   , required): SQLAlchemy session for database connection.
            where           (Union[List[Dict[str, Any]],
                                        Dict[str, Any]], required): List of filter conditions. Defaults to None.
            allow_no_result (bool                      , optional): Allow no result. Defaults to True.

        Raises:
            NoResultFound: If object doesn't exist in database and `allow_no_result` is False.

        Returns:
            Union[DeclarativeBase, None]: ORM object or None.
        """

        _orm_object: Union[cls, None] = None
        try:
            _orm_objects: List[cls] = cls.select_by_where(
                session=session,
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


__all__ = ["ReadMixin"]
