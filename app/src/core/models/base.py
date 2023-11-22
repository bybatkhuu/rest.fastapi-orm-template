# -*- coding: utf-8 -*-

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs

from src.config import config
from src.core import utils
from src.databases.rdb.mixins import CRUDMixin


_NAMING_CONVENTION = {
    "ix": "idx_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class BaseORM(CRUDMixin, AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention=_NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        _table_name = utils.camel_to_snake(cls.__name__).replace("_orm", "")
        _table_name = f"{config.db.table_prefix}{_table_name}"
        return _table_name


__all__ = ["BaseORM"]
