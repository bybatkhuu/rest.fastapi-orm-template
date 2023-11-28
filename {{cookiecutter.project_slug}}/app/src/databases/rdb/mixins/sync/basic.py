# -*- coding: utf-8 -*-

from typing import Union, List, Dict, Any

from sqlalchemy import func, Select, select, Result
from sqlalchemy.orm import declarative_mixin, Session

from src.databases.rdb.mixins import BaseMixin
from src.logger import logger


@declarative_mixin
class BasicMixin(BaseMixin):
    @classmethod
    def exists_by_id(cls, session: Session, id: str) -> bool:
        """Check if ORM object exists in database by ID.

        Args:
            session (Session, required): SQLAlchemy session for database connection.
            id      (str         , required): ID of object.

        Raises:
            Exception: If failed to check if ORM object exists in database by ID.

        Returns:
            bool: True if exists, False otherwise.
        """

        _is_exists = False
        try:
            _stmt: Select = select(cls.id).where(cls.id == id)
            _result: Result = session.execute(_stmt)
            if _result.scalar():
                _is_exists = True
        except Exception:
            logger.error(
                f"Failed to check if '{cls.__name__}' object '{id}' ID exists in database!"
            )
            raise

        return _is_exists

    def exists(self, session: Session) -> bool:
        """Check if ORM object exists in database.

        Args:
            session (Session, required): SQLAlchemy session for database connection.

        Raises:
            Exception: If failed to check if ORM object exists in database.

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

            _result: Result = session.execute(_stmt)
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

        Raises:
            Exception: If failed to count ORM objects in database.

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


__all__ = ["BasicMixin"]
