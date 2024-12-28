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
    asc,
    inspect,
    Select,
    select,
    Insert,
    Update,
    Delete,
    Subquery,
)
from sqlalchemy.orm import DeclarativeBase, declarative_mixin, Mapped, mapped_column
from sqlalchemy.util import ReadOnlyProperties

from src.core.constants import OrderDirect, WarnEnum
from src.config import config
from src.core import utils
from src.logger import logger


@declarative_mixin
class IdStrMixin:
    id: Mapped[str] = mapped_column(String(64), primary_key=True, sort_order=-100)


@declarative_mixin
class IdIntMixin:
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, sort_order=-100
    )


@declarative_mixin
class TimestampMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.CURRENT_TIMESTAMP(),
        sort_order=1001,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.CURRENT_TIMESTAMP(),
        sort_order=1002,
    )

    __table_args__ = (Index("idx_created_at_desc", desc("created_at")),)


@declarative_mixin
class BaseMixin(TimestampMixin, IdStrMixin):
    def __init__(self, warn_mode: WarnEnum = WarnEnum.ALWAYS, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = self.__class__.create_unique_id()

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


__all__ = ["BaseMixin"]
