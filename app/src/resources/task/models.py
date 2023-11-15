# -*- coding: utf-8 -*-

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import AsyncBaseORM


class TaskORM(AsyncBaseORM):
    name: Mapped[str] = mapped_column(String(64), nullable=False)


__all__ = ["TaskORM"]
