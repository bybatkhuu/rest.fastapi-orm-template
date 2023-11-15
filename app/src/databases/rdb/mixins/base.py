# -*- coding: utf-8 -*-

import json
from datetime import datetime
from typing import Union, List, Dict, Any

from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    Index,
    func,
    desc,
    inspect,
    Select,
    select,
    Insert,
    Update,
    Delete,
    ChunkedIteratorResult,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    declarative_mixin,
    Mapped,
    mapped_column,
    Session,
)
from sqlalchemy.util import ReadOnlyProperties
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import WarnEnum
from src.core import utils
from src.logger import logger


@declarative_mixin
class IdIntMixin:
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, sort_order=-10
    )


@declarative_mixin
class IdStrMixin:
    id: Mapped[str] = mapped_column(String(64), primary_key=True, sort_order=-10)


@declarative_mixin
class TimestampMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.CURRENT_TIMESTAMP(),
        sort_order=9998,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.CURRENT_TIMESTAMP(),
        sort_order=9999,
    )

    __table_args__ = (
        Index(None, desc("created_at")),
    )


@declarative_mixin
class BaseMixin(TimestampMixin, IdStrMixin):
    def __init__(self, warn_mode: WarnEnum = WarnEnum.ALWAYS, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = self.__class__.create_unique_id()

        _now_utc_tz = utils.now_utc_tz()
        if "created_at" not in kwargs:
            kwargs["created_at"] = _now_utc_tz

        if "updated_at" not in kwargs:
            kwargs["updated_at"] = _now_utc_tz

        for _key, _val in kwargs.items():
            try:
                getattr(self, _key)
                setattr(self, _key, _val)
            except AttributeError:
                _message = f"Not found '{_key}' attribute in `{self.__class__.__name__}` class."
                if warn_mode == WarnEnum.ALWAYS:
                    logger.warning(_message)
                elif warn_mode == WarnEnum.DEBUG:
                    logger.debug(_message)
                elif warn_mode == WarnEnum.ERROR:
                    logger.error(_message)
                    raise

        super().__init__()

    @classmethod
    def create_unique_id(cls) -> str:
        """Create unique ID for ORM object.

        Returns:
            str: Unique ID.
        """

        _prefix = cls.__name__[0:3]
        _id = utils.create_unique_id(prefix=_prefix)
        return _id

    def to_dict(self) -> Dict[str, Any]:
        """Convert ORM object to dictionary.

        Returns:
            Dict[str, Any]: Dictionary of ORM object.
        """

        _dict = {}
        _columns: ReadOnlyProperties = inspect(self).mapper.column_attrs
        for _column in _columns:
            _dict[_column.key] = getattr(self, _column.key)

        return _dict

    def to_json(self) -> str:
        """Convert ORM object to JSON string.

        Returns:
            str: JSON string of ORM object.
        """

        _json = json.dumps(self.to_dict(), default=str, ensure_ascii=False)
        return _json

    @classmethod
    def from_json(cls, json_str: str) -> DeclarativeBase:
        """Convert JSON string to ORM object.

        Args:
            json_str (str, required): JSON string.

        Returns:
            DeclarativeBase: ORM object.
        """

        _dict = json.loads(json_str)
        _orm_object = cls(**_dict)
        return _orm_object

    def __str__(self) -> str:
        """Convert ORM object to string representation.

        Returns:
            str: String representation of ORM object.
        """

        _str = self.to_json()
        return _str

    @classmethod
    def _build_where(
        cls,
        stmt: Union[Select, Insert, Update, Delete],
        where: Union[List[Dict[str, Any]], Dict[str, Any]],
    ) -> Union[Select, Insert, Update, Delete]:
        """Build SQLAlchemy SQL statement with `where` filter conditions.

        Args:
            stmt  (Union[Select, Insert, Update, Delete], required): SQLAlchemy SQL statement.
            where (Union[List[Dict[str, Any]],
                              Dict[str, Any]]           , required): List of filter conditions

        Raises:
            ValueError: If `column` or `value` key doesn't exist in `where` filter.

        Returns:
            Union[Select, Insert, Update, Delete]: Built SQLAlchemy SQL statement.
        """

        if isinstance(where, dict):
            where = [where]

        for _where in where:
            if "column" not in _where:
                raise ValueError("Not found 'column' key in 'where'!")

            if "value" not in _where:
                raise ValueError("Not found 'value' key in 'where'!")

            if (
                ("op" not in _where)
                or (_where["op"] == "eq")
                or (_where["op"] == "equal")
                or (_where["op"] == "=")
                or (_where["op"] == "==")
            ):
                stmt = stmt.where(getattr(cls, _where["column"]) == _where["value"])
            elif _where["op"] == "like":
                stmt = stmt.where(
                    getattr(cls, _where["column"]).like(f'%{_where["value"]}%')
                )
            elif (_where["op"] == "gt") or (_where["op"] == ">"):
                stmt = stmt.where(getattr(cls, _where["column"]) > _where["value"])
            elif (_where["op"] == "ge") or (_where["op"] == ">="):
                stmt = stmt.where(getattr(cls, _where["column"]) >= _where["value"])
            elif (_where["op"] == "lt") or (_where["op"] == "<"):
                stmt = stmt.where(getattr(cls, _where["column"]) < _where["value"])
            elif (_where["op"] == "le") or (_where["op"] == "<="):
                stmt = stmt.where(getattr(cls, _where["column"]) <= _where["value"])
            elif _where["op"] == "between":
                stmt = stmt.where(
                    getattr(cls, _where["column"]).between(
                        _where["value"][0], _where["value"][1]
                    )
                )

        return stmt

    ## Async
    @classmethod
    async def async_exists_by_id(cls, async_session: AsyncSession, id: str) -> bool:
        """Check if ORM object exists in database by ID.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
            id            (str         , required): ID of object.

        Returns:
            bool: True if exists, False otherwise.
        """

        _is_exists = False
        try:
            _stmt: Select = select(cls.id).where(cls.id == id)
            _result: ChunkedIteratorResult = await async_session.execute(_stmt)
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

        Returns:
            int: Count of ORM objects in database.
        """

        _count = 0
        try:
            _stmt: Select = select(func.count()).select_from(cls)
            if where:
                _stmt: Select = cls._build_where(stmt=_stmt, where=where)

            _result: ChunkedIteratorResult = await async_session.execute(_stmt)
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

    ## Sync
    @classmethod
    def exists_by_id(cls, session: Session, id: str) -> bool:
        """Check if ORM object ID exists in database.

        Args:
            session (Session, required): SQLAlchemy session for database connection.
            id      (str    , required): ID of object.

        Returns:
            bool: True if exists, False otherwise.
        """

        _is_exists = False
        try:
            _stmt: Select = select(cls.id).where(cls.id == id)
            _result: ChunkedIteratorResult = session.execute(_stmt)
            if _result.scalar():
                _is_exists = True
        except Exception:
            logger.error(
                f"Failed to check if '{cls.__name__}' object '{id}' ID exists in database!"
            )
            raise

        return _is_exists

    def exists(self, session: Session) -> bool:
        """Check if ORM object ID exists in database.

        Args:
            session (Session, required): SQLAlchemy session for database connection.

        Returns:
            bool: True if exists, False otherwise.
        """

        _is_exists = False
        try:
            _is_exists = self.__class__.exists_by_id(session=session, id=self.id)
        except Exception:
            logger.error(
                f"Failed to check if '{self.__class__.__name__}' object '{self.id}' ID exists in database!"
            )
            raise

        return _is_exists

    @classmethod
    def count_by_where(
        cls,
        session: Session,
        where: Union[List[Dict[str, Any]], Dict[str, Any]],
    ) -> int:
        """Count ORM objects in database by filter conditions.

        Args:
            session (Session                   , required): SQLAlchemy session for database connection.
            where   (Union[List[Dict[str, Any]],
                                Dict[str, Any]], required): List of filter conditions.

        Returns:
            int: Count of ORM objects in database.
        """

        _count = 0
        try:
            _stmt: Select = select(func.count()).select_from(cls)
            if where:
                _stmt: Select = cls._build_where(stmt=_stmt, where=where)

            _result: ChunkedIteratorResult = session.execute(_stmt)
            _count: int = _result.scalar()
        except Exception:
            logger.error(
                f"Failed to count '{cls.__name__}' objects by '{where}' filter in database!"
            )
            raise

        return _count

    @classmethod
    def count(cls, session: Session) -> int:
        """Count all ORM objects in database.

        Args:
            session (Session, required): SQLAlchemy session for database connection.

        Returns:
            int: Count of ORM objects in database.
        """

        _count = 0
        try:
            _count: int = cls.count_by_where(session=session, where=[])
        except Exception:
            logger.error(f"Failed to count '{cls.__name__}' objects from database!")
            raise

        return _count


__all__ = ["IdIntMixin", "IdStrMixin", "TimestampMixin", "BaseMixin"]
