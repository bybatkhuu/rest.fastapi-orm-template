# -*- coding: utf-8 -*-

from sqlalchemy.orm import declarative_mixin

from .async_ import AsyncCreateMixin, AsyncDeleteMixin
from .sync import CreateMixin, DeleteMixin


@declarative_mixin
class CRUDMixin(AsyncCreateMixin, AsyncDeleteMixin, CreateMixin, DeleteMixin):
    pass


__all__ = ["CRUDMixin"]
