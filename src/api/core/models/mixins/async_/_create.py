# -*- coding: utf-8 -*-

from typing import Any, Dict, Union, List

from pydantic import validate_call
from sqlalchemy import Result
from sqlalchemy.orm import DeclarativeBase, declarative_mixin
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import WarnEnum
from api.config import config

if config.db.dialect == "postgresql":
    from sqlalchemy.dialects.postgresql import Insert, insert
    from psycopg.errors import (
        NotNullViolation,
        UniqueViolation,
        ForeignKeyViolation,
        CheckViolation,
    )
elif (config.db.dialect == "mysql") or (config.db.dialect == "mariadb"):
    from sqlalchemy.dialects.mysql import Insert, insert
else:
    from sqlalchemy import Insert, insert
from api.core.exceptions import (
    EmptyValueError,
    PrimaryKeyError,
    UniqueKeyError,
    NullConstraintError,
    ForeignKeyError,
    CheckConstraintError,
)
from api.logger import logger

from ._update import AsyncUpdateMixin


@declarative_mixin
class AsyncCreateMixin(AsyncUpdateMixin):
    @classmethod
    @validate_call(config={"arbitrary_types_allowed": True})
    async def async_insert(
        cls,
        async_session: AsyncSession,
        orm_way: bool = False,
        returning: bool = True,
        auto_commit: bool = False,
        warn_mode: WarnEnum = WarnEnum.DEBUG,
        **kwargs,
    ) -> DeclarativeBase:
        """Insert new data/ORM object into database.

        Args:
            async_session (AsyncSession  , required): SQLAlchemy async_session for database connection.
            orm_way       (bool          , optional): Use ORM way to insert object into database. Defaults to False.
            returning     (bool          , optional): Return inserted ORM object from database. Defaults to True.
            auto_commit   (bool          , optional): Auto commit. Defaults to False.
            warn_mode     (WarnEnum      , optional): Warning mode. Defaults to `WarnEnum.DEBUG`.
            **kwargs      (Dict[str, Any], required): Dictionary of object data.

        Raises:
            EmptyValueError     : If no data provided to insert.
            NullConstraintError : If null constraint error occurred.
            PrimaryKeyError     : If ID (PK) already exists in database.
            UniqueKeyError      : If unique constraint error occurred.
            ForeignKeyError     : If foreign key constraint error occurred.
            CheckConstraintError: If check constraint error occurred.
            Exception           : If failed to save object into database.

        Returns:
            DeclarativeBase: New ORM object.
        """

        if not kwargs:
            raise EmptyValueError("No data provided to insert!")

        if "id" not in kwargs:
            kwargs["id"] = cls.gen_unique_id()

        _orm_object: Union[DeclarativeBase, None] = None
        try:
            if orm_way:
                _orm_object = cls(**kwargs)
                async_session.add(_orm_object)

                if auto_commit:
                    await async_session.commit()

            else:
                _stmt: Insert = insert(cls).values(**kwargs)
                if returning:
                    _stmt = _stmt.returning(cls)

                _result: Result = await async_session.execute(_stmt)
                if returning:
                    _orm_object: cls = _result.scalars().one()

                if auto_commit:
                    await async_session.commit()

        except Exception as err:
            if auto_commit:
                await async_session.rollback()

            if isinstance(err, IntegrityError):
                if isinstance(err.orig, NotNullViolation):
                    raise NullConstraintError(
                        f"`{err.orig.diag.column_name}` cannot be NULL."
                    )
                elif isinstance(err.orig, UniqueViolation):
                    _detail = err.orig.diag.message_detail.replace("Key ", "")
                    if "(id)=" in _detail:
                        logger.error(
                            f"`{cls.__name__}` '{kwargs['id']}' ID already exists in database!"
                        )
                        raise PrimaryKeyError(_detail)

                    raise UniqueKeyError(_detail)
                elif isinstance(err.orig, ForeignKeyViolation):
                    _detail = (
                        err.orig.diag.message_detail.replace("Key ", "")
                        .replace('"', "'")
                        .replace(f"table '{config.db.prefix}", "'")
                    )
                    raise ForeignKeyError(_detail)
                elif isinstance(err.orig, CheckViolation):
                    _detail = err.orig.diag.message_detail.replace("Key ", "")
                    raise CheckConstraintError(_detail)

            _message = f"Failed to insert `{cls.__name__}` object '{kwargs['id']}' ID into database!"
            if warn_mode == WarnEnum.ALWAYS:
                logger.error(_message)
            if warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            raise

        return _orm_object

    @validate_call(config={"arbitrary_types_allowed": True})
    async def async_save(
        self,
        async_session: AsyncSession,
        auto_commit: bool = False,
        warn_mode: WarnEnum = WarnEnum.DEBUG,
        **kwargs,
    ) -> DeclarativeBase:
        """Save ORM object into database.

        Args:
            async_session (AsyncSession  , required): SQLAlchemy async_session for database connection.
            auto_commit   (bool          , optional): Auto commit. Defaults to False.
            warn_mode     (WarnEnum      , optional): Warning mode. Defaults to `WarnEnum.DEBUG`.
            **kwargs      (Dict[str, Any], optional): Dictionary of ORM object data.

        Raises:
            NullConstraintError : If null constraint error occurred.
            PrimaryKeyError     : If ID (PK) already exists in database.
            UniqueKeyError      : If unique constraint error occurred.
            ForeignKeyError     : If foreign key constraint error occurred.
            CheckConstraintError: If check constraint error occurred.
            Exception           : If failed to save object into database.

        Returns:
            DeclarativeBase: Created or updated ORM object.
        """

        try:
            for _key, _val in kwargs.items():
                setattr(self, _key, _val)

            _orm_object: Union[DeclarativeBase, None] = await self.__class__.async_get(
                async_session=async_session,
                id=self.id,
                allow_no_result=True,
                warn_mode=WarnEnum.IGNORE,
            )

            if not _orm_object:
                async_session.add(self)

            if auto_commit:
                await async_session.commit()

        except Exception as err:
            if auto_commit:
                await async_session.rollback()

            if isinstance(err, IntegrityError):
                if isinstance(err.orig, NotNullViolation):
                    raise NullConstraintError(
                        f"`{err.orig.diag.column_name}` cannot be NULL."
                    )
                elif isinstance(err.orig, UniqueViolation):
                    _detail = err.orig.diag.message_detail.replace("Key ", "")
                    if "(id)=" in _detail:
                        logger.error(
                            f"`{self.__class__.__name__}` '{self.id}' ID already exists in database!"
                        )
                        raise PrimaryKeyError(_detail)

                    raise UniqueKeyError(_detail)
                elif isinstance(err.orig, ForeignKeyViolation):
                    _detail = (
                        err.orig.diag.message_detail.replace("Key ", "")
                        .replace('"', "'")
                        .replace(f"table '{config.db.prefix}", "'")
                    )
                    raise ForeignKeyError(_detail)
                elif isinstance(err.orig, CheckViolation):
                    _detail = err.orig.diag.message_detail.replace("Key ", "")
                    raise CheckConstraintError(_detail)

            _message = f"Failed to save `{self.__class__.__name__}` object (self) '{self.id}' ID into database!"
            if warn_mode == WarnEnum.ALWAYS:
                logger.error(_message)
            if warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            raise

        return self

    @classmethod
    @validate_call(config={"arbitrary_types_allowed": True})
    async def async_upsert(
        cls,
        async_session: AsyncSession,
        orm_way: bool = False,
        returning: bool = True,
        auto_commit: bool = False,
        warn_mode: WarnEnum = WarnEnum.DEBUG,
        **kwargs,
    ) -> Union[DeclarativeBase, None]:
        """Upsert data into database.

        Args:
            async_session (AsyncSession, required): SQLAlchemy async_session for database connection.
            orm_way       (bool        , optional): Check if object exists in database. Defaults to False.
            returning     (bool        , optional): Return upserted ORM object from database. Defaults to True.
            auto_commit   (bool        , optional): Auto commit. Defaults to False.
            warn_mode     (WarnEnum    , optional): Warning mode. Defaults to `WarnEnum.DEBUG`.
            **kwargs      (Dict        , required): Dictionary of object data.

        Raises:
            EmptyValueError     : If no data provided to upsert.
            NullConstraintError : If null constraint error occurred.
            UniqueKeyError      : If unique constraint error occurred.
            ForeignKeyError     : If foreign key constraint error occurred.
            CheckConstraintError: If check constraint error occurred.
            Exception           : If failed to upsert object into database.

        Returns:
            Union[DeclarativeBase, None]: Upserted ORM object.
        """

        if not kwargs:
            raise EmptyValueError("No data provided to upsert!")

        _orm_object: Union[cls, None] = None
        if orm_way:
            if "id" in kwargs:
                _orm_object: Union[cls, None] = await cls.async_get(
                    async_session=async_session,
                    id=kwargs["id"],
                    allow_no_result=True,
                    warn_mode=warn_mode,
                )

            if _orm_object:
                _orm_object: cls = await _orm_object.async_update(
                    async_session=async_session,
                    auto_commit=auto_commit,
                    warn_mode=warn_mode,
                    **kwargs,
                )
            else:
                _orm_object: cls = await cls.async_insert(
                    async_session=async_session,
                    orm_way=True,
                    auto_commit=auto_commit,
                    warn_mode=warn_mode,
                    **kwargs,
                )
        else:
            try:
                if "id" not in kwargs:
                    kwargs["id"] = cls.gen_unique_id()

                _update_set = {
                    key: value for key, value in kwargs.items() if key != "id"
                }

                _stmt: Insert = insert(cls).values(**kwargs)
                # Only for PostgreSQL
                if config.db.dialect == "postgresql":
                    _stmt = _stmt.on_conflict_do_update(
                        index_elements=["id"], set_=_update_set
                    )
                # Only for MySQL and MariaDB
                elif (config.db.dialect == "mysql") or (config.db.dialect == "mariadb"):
                    _stmt = _stmt.on_duplicate_key_update(**_update_set)

                if returning:
                    _stmt = _stmt.returning(cls)

                _result: Result = await async_session.execute(_stmt)
                if returning:
                    _orm_object: cls = _result.scalars().one()

                if auto_commit:
                    await async_session.commit()

            except Exception as err:
                if auto_commit:
                    await async_session.rollback()

                if isinstance(err, IntegrityError):
                    if isinstance(err.orig, NotNullViolation):
                        raise NullConstraintError(
                            f"`{err.orig.diag.column_name}` cannot be NULL."
                        )
                    elif isinstance(err.orig, UniqueViolation):
                        _detail = err.orig.diag.message_detail.replace("Key ", "")
                        raise UniqueKeyError(_detail)
                    elif isinstance(err.orig, ForeignKeyViolation):
                        _detail = (
                            err.orig.diag.message_detail.replace("Key ", "")
                            .replace('"', "'")
                            .replace(f"table '{config.db.prefix}", "'")
                        )
                        raise ForeignKeyError(_detail)
                    elif isinstance(err.orig, CheckViolation):
                        _detail = err.orig.diag.message_detail.replace("Key ", "")
                        raise CheckConstraintError(_detail)

                _message = f"Failed to upsert `{cls.__name__}` object '{kwargs['id']}' ID into database!"
                if warn_mode == WarnEnum.ALWAYS:
                    logger.error(_message)
                if warn_mode == WarnEnum.DEBUG:
                    logger.debug(_message)

                raise

        return _orm_object

    @classmethod
    @validate_call(config={"arbitrary_types_allowed": True})
    async def async_bulk_insert(
        cls,
        async_session: AsyncSession,
        raw_data: List[Dict[str, Any]],
        returning: bool = True,
        auto_commit: bool = False,
        warn_mode: WarnEnum = WarnEnum.DEBUG,
    ) -> List[DeclarativeBase]:
        """Bulk insert data into database.

        Args:
            async_session (AsyncSession        , required): SQLAlchemy async_session for database connection.
            raw_data      (List[Dict[str, Any]], required): List of dictionary object data.
            returning     (bool                , optional): Return inserted ORM objects from database. Defaults to True.
            auto_commit   (bool                , optional): Auto commit. Defaults to False.
            warn_mode     (WarnEnum            , optional): Warning mode. Defaults to `WarnEnum.DEBUG`.

        Raises:
            EmptyValueError     : If no data provided to bulk insert.
            NullConstraintError : If null constraint error occurred.
            PrimaryKeyError     : If ID (PK) already exists in database.
            UniqueKeyError      : If unique constraint error occurred.
            ForeignKeyError     : If foreign key constraint error occurred.
            CheckConstraintError: If check constraint error occurred.
            Exception           : If failed to bulk insert objects into database.

        Returns:
            List[DeclarativeBase]: List of inserted ORM objects.
        """

        if not raw_data:
            raise EmptyValueError("No data provided to bulk insert!")

        for _data in raw_data:
            if "id" not in _data:
                _data["id"] = cls.gen_unique_id()

        _orm_objects: List[cls] = []
        try:
            _stmt: Insert = insert(cls)
            if returning:
                _stmt = _stmt.returning(cls)

            _result: Result = await async_session.execute(_stmt, raw_data)
            if returning:
                _orm_objects: List[cls] = _result.scalars().all()

            if auto_commit:
                await async_session.commit()

        except Exception as err:
            if auto_commit:
                await async_session.rollback()

            if isinstance(err, IntegrityError):
                if isinstance(err.orig, NotNullViolation):
                    raise NullConstraintError(
                        f"`{err.orig.diag.column_name}` cannot be NULL."
                    )
                elif isinstance(err.orig, UniqueViolation):
                    _detail = err.orig.diag.message_detail.replace("Key ", "")
                    if "(id)=" in _detail:
                        logger.error(
                            f"`{cls.__name__}` IDs already exists in database!"
                        )
                        raise PrimaryKeyError(_detail)

                    raise UniqueKeyError(_detail)
                elif isinstance(err.orig, ForeignKeyViolation):
                    _detail = (
                        err.orig.diag.message_detail.replace("Key ", "")
                        .replace('"', "'")
                        .replace(f"table '{config.db.prefix}", "'")
                    )
                    raise ForeignKeyError(_detail)
                elif isinstance(err.orig, CheckViolation):
                    _detail = err.orig.diag.message_detail.replace("Key ", "")
                    raise CheckConstraintError(_detail)

            _message = f"Failed to bulk insert `{cls.__name__}` objects into database!"
            if warn_mode == WarnEnum.ALWAYS:
                logger.error(_message)
            if warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            raise

        return _orm_objects


__all__ = ["AsyncCreateMixin"]
