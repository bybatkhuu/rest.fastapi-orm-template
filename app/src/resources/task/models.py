# -*- coding: utf-8 -*-

from sqlalchemy import String, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import AsyncBaseORM


class TaskORM(AsyncBaseORM):
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    point: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )


__all__ = ["TaskORM"]
