# -*- coding: utf-8 -*-

from sqlalchemy.orm import declarative_mixin

from .async_ import AsyncCreateMixin, AsyncDeleteMixin
from .sync import CreateMixin, DeleteMixin


@declarative_mixin
class AsyncCRUDMixin(AsyncCreateMixin, AsyncDeleteMixin):
    pass


@declarative_mixin
class CRUDMixin(CreateMixin, DeleteMixin):
    pass


__all__ = [
    "AsyncCRUDMixin",
    "CRUDMixin",
]
