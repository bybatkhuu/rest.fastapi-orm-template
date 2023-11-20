# -*- coding: utf-8 -*-

from typing import List, Dict, Union, Any

from sqlalchemy import Update, update, Result
from sqlalchemy.orm import Session, DeclarativeBase, declarative_mixin
from sqlalchemy.exc import NoResultFound

from src.logger import logger

from .read import ReadMixin


@declarative_mixin
class UpdateMixin(ReadMixin):
    def update(
        self,
        session: Session,
        auto_commit: bool = True,
        returning: bool = False,
        **kwargs: Dict[str, Any],
    ) -> DeclarativeBase:
        """Update ORM object into database.

        Args:
            session     (Session       , required): SQLAlchemy session for database connection.
            auto_commit (bool          , optional): Auto commit. Defaults to True.
            returning   (bool          , optional): Return updated ORM object. Defaults to False.
            **kwargs    (Dict[str, Any], optional): Dictionary of update data.

        Raises:
            Exception : If failed to update object into database.

        Returns:
            DeclarativeBase: Updated ORM object.
        """

        try:
            for _key, _val in kwargs.items():
                if _key == "id":
                    continue
                else:
                    setattr(self, _key, _val)

            if auto_commit:
                session.commit()
                if returning:
                    session.refresh(self)
        except Exception:
            if auto_commit:
                session.rollback()

            logger.error(
                f"Failed to update '{self.__class__.__name__}' object '{self.id}' ID into database!"
            )
            raise

        return self

    @classmethod
    def update_by_id(
        cls,
        session: Session,
        id: str,
        orm_way: bool = False,
        auto_commit: bool = True,
        returning: bool = True,
        **kwargs: Dict[str, Any],
    ) -> DeclarativeBase:
        """Update ORM object into database by ID.

        Args:
            session     (Session       , required): SQLAlchemy session for database connection.
            id          (str           , required): ID of object.
            orm_way     (bool          , optional): Use ORM way to update object into database. Defaults to False.
            auto_commit (bool          , optional): Auto commit. Defaults to True.
            returning   (bool          , optional): Return updated ORM object. Defaults to True.
            **kwargs    (Dict[str, Any], required): Dictionary of update data.

        Raises:
            ValueError   : If no data provided to update.
            NoResultFound: If ORM object ID not found in database, when `orm_way` is True.
            Exception    : If failed to update object into database.

        Returns:
            DeclarativeBase: Updated ORM object.
        """

        if not kwargs:
            raise ValueError("No data provided to update!")

        _orm_object: Union[cls, None] = None
        try:
            if orm_way:
                _orm_object: cls = cls.get(
                    session=session, id=id, allow_no_result=False
                )
                _orm_object: cls = _orm_object.update(
                    session=session,
                    auto_commit=auto_commit,
                    returning=returning,
                    **kwargs,
                )
            else:
                _stmt: Update = update(cls).where(cls.id == id).values(**kwargs)
                if returning:
                    _stmt = _stmt.returning(cls)

                _result: Result = session.execute(_stmt)
                if returning:
                    _orm_object: Union[cls, None] = _result.scalars().one()

                if auto_commit:
                    session.commit()

                if not returning:
                    logger.debug(
                        f"Updated '{_result.rowcount}' row(s) into '{cls.__name__}' table."
                    )

                    if _result.rowcount == 0:
                        raise NoResultFound(
                            f"Not found any '{cls.__name__}' object with '{id}' ID from database!"
                        )
        except NoResultFound:
            if (not orm_way) and auto_commit:
                session.rollback()

            raise
        except Exception:
            if (not orm_way) and auto_commit:
                session.rollback()

            logger.error(
                f"Failed to update '{cls.__name__}' object with '{id}' ID into database!"
            )
            raise

        return _orm_object

    @classmethod
    def update_by_ids(
        cls,
        session: Session,
        ids: List[str],
        auto_commit: bool = True,
        returning: bool = True,
        **kwargs: Dict[str, Any],
    ) -> List[DeclarativeBase]:
        """Update ORM objects into database by ID list.

        Args:
            session     (Session       , required): SQLAlchemy session for database connection.
            ids         (List[str]     , required): List of IDs.
            auto_commit (bool          , optional): Auto commit. Defaults to True.
            returning   (bool          , optional): Return updated ORM object. Defaults to True.
            **kwargs    (Dict[str, Any], required): Dictionary of update data.

        Raises:
            ValueError: If no data provided to update.
            Exception : If failed to update objects into database.

        Returns:
            List[DeclarativeBase]: List of updated ORM objects.
        """

        if not kwargs:
            raise ValueError("No data provided to update!")

        _orm_objects: List[cls] = []
        if 0 < len(ids):
            try:
                _stmt: Update = update(cls).where(cls.id.in_(ids)).values(**kwargs)
                if returning:
                    _stmt = _stmt.returning(cls)

                _result: Result = session.execute(_stmt)
                if returning:
                    _orm_objects: List[cls] = _result.scalars().all()

                if auto_commit:
                    session.commit()

                if not returning:
                    logger.debug(
                        f"Updated '{_result.rowcount}' row(s) into '{cls.__name__}' table."
                    )
            except Exception:
                if auto_commit:
                    session.rollback()

                logger.error(
                    f"Failed to update '{cls.__name__}' objects by ID list into database!"
                )
                raise

        return _orm_objects

    @classmethod
    def update_objects(
        cls,
        session: Session,
        orm_objects: List[DeclarativeBase],
        auto_commit: bool = True,
        returning: bool = False,
        **kwargs: Dict[str, Any],
    ) -> List[DeclarativeBase]:
        """Update ORM objects into database.

        Args:
            session     (Session              , required): SQLAlchemy session for database connection.
            orm_objects (List[DeclarativeBase], required): List of ORM objects.
            auto_commit (bool                 , optional): Auto commit. Defaults to True.
            returning   (bool                 , optional): Return updated ORM object. Defaults to False.
            **kwargs    (Dict[str, Any]       , required): Dictionary of update data.

        Raises:
            ValueError: If no data provided to update.
            Exception : If failed to update objects into database.

        Returns:
            List[DeclarativeBase]: List of updated ORM objects.
        """

        if not kwargs:
            raise ValueError("No data provided to update!")

        if 0 < len(orm_objects):
            try:
                for _orm_object in orm_objects:
                    for _key, _val in kwargs.items():
                        if _key == "id":
                            continue
                        elif _val is not None:
                            setattr(_orm_object, _key, _val)

                if auto_commit:
                    session.commit()
                    if returning:
                        for _orm_object in orm_objects:
                            session.refresh(_orm_object)
            except Exception:
                if auto_commit:
                    session.rollback()

                logger.error(
                    f"Failed to update '{cls.__name__}' objects into database!"
                )
                raise

        return orm_objects

    @classmethod
    def update_by_where(
        cls,
        session: Session,
        where: Union[List[Dict[str, Any]], Dict[str, Any]],
        orm_way: bool = False,
        auto_commit: bool = True,
        returning: bool = True,
        **kwargs: Dict[str, Any],
    ) -> List[DeclarativeBase]:
        """Update ORM objects into database by filter conditions.

        Args:
            session     (Session                   , required): SQLAlchemy session for database connection.
            where       (Union[List[Dict[str, Any]],
                                    Dict[str, Any]], required): List of filter conditions.
            orm_way     (bool                      , optional): Use ORM way to update object into database. Defaults to False.
            auto_commit (bool                      , optional): Auto commit. Defaults to True.
            returning   (bool                      , optional): Return updated ORM object. Defaults to True.
            **kwargs    (Dict[str, Any]            , required): Dictionary of update data.

        Raises:
            ValueError: If no data provided to update.
            Exception : If failed to update objects into database.

        Returns:
            List[DeclarativeBase]: List of updated ORM objects.
        """

        if not kwargs:
            raise ValueError("No data provided to update!")

        _orm_objects: List[cls] = []
        try:
            if orm_way:
                _orm_objects: List[cls] = cls.select_by_where(
                    session=session, where=where, disable_limit=True
                )

                if 0 < len(_orm_objects):
                    _orm_objects: List[cls] = cls.update_objects(
                        session=session,
                        objects=_orm_objects,
                        auto_commit=auto_commit,
                        returning=returning,
                        **kwargs,
                    )
            else:
                _stmt: Update = update(cls)
                _stmt = cls._build_where(_stmt, where)
                _stmt = _stmt.values(**kwargs)
                if returning:
                    _stmt = _stmt.returning(cls)

                _result: Result = session.execute(_stmt)
                if returning:
                    _orm_objects: List[cls] = _result.scalars().all()

                if auto_commit:
                    session.commit()

                if not returning:
                    logger.debug(
                        f"Updated '{_result.rowcount}' row(s) into '{cls.__name__}' table."
                    )
        except Exception:
            if (not orm_way) and auto_commit:
                session.rollback()

            logger.error(
                f"Failed to update '{cls.__name__}' object by '{where}' filter into database!"
            )
            raise

        return _orm_objects

    @classmethod
    def update_all(
        cls,
        session: Session,
        auto_commit: bool = True,
        **kwargs: Dict[str, Any],
    ):
        """Update all current table ORM objects in database.

        Args:
            session     (Session       , required): SQLAlchemy session for database connection.
            auto_commit (bool          , optional): Auto commit. Defaults to True.
            **kwargs    (Dict[str, Any], required): Dictionary of update data.

        Raises:
            ValueError: If no data provided to update.
            Exception : If failed to update objects into database.
        """

        if not kwargs:
            raise ValueError("No data provided to update!")

        try:
            _stmt: Update = update(cls).values(**kwargs)
            _result: Result = session.execute(_stmt)

            if auto_commit:
                session.commit()

            logger.debug(
                f"Updated '{_result.rowcount}' row(s) into '{cls.__name__}' table."
            )
        except Exception:
            if auto_commit:
                session.rollback()

            logger.error(f"Failed to update '{cls.__name__}' objects into database!")
            raise


__all__ = ["UpdateMixin"]
