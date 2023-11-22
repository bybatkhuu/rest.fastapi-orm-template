# -*- coding: utf-8 -*-

from typing import List, Tuple

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import validate_arguments

from src.core.constants import ErrorCodeEnum
from src.config import config
from src.core.exceptions import BaseHTTPException
from src.resources.task.schemas import TaskBasePM
from src.resources.task.models import TaskORM
from src.logger import logger


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def async_get_list(
    db_session: AsyncSession,
    request_id: str,
    skip: int = 0,
    limit: int = config.db.select_limit,
    **kwargs,
) -> Tuple[List[TaskORM], int]:
    _total_count = 0
    _tasks: List[TaskORM] = []
    try:
        _where = []
        if kwargs:
            for _key, _val in kwargs.items():
                if _key == "name":
                    _where.append({"op": "like", "column": _key, "value": _val})
                else:
                    _where.append({"column": _key, "value": _val})

        _tasks: List[TaskORM] = await TaskORM.async_select_by_where(
            async_session=db_session, where=_where, offset=skip, limit=limit
        )
        _total_count: int = await TaskORM.async_count_by_where(
            async_session=db_session, where=_where
        )

    except Exception:
        logger.exception(f"[{request_id}] - Failed to get task list from database!")
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.DATABASE_ERROR,
            message="Failed to get task list!",
        )

    return _tasks, _total_count


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def async_create(
    db_session: AsyncSession,
    request_id: str,
    task_in: TaskBasePM,
) -> TaskORM:
    _task: TaskORM
    try:
        _task: TaskORM = await TaskORM.async_insert(
            async_session=db_session, **task_in.dict()
        )
    except IntegrityError:
        logger.exception(f"[{request_id}] - Task ID conflict!")
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.DATABASE_ERROR,
            message=f"Failed to create task because of ID conflict!",
        )
    except Exception:
        logger.exception(
            f"[{request_id}] - Failed to create and save task data into database!"
        )
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.DATABASE_ERROR,
            message=f"Failed to create task!",
        )

    return _task


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def async_get(db_session: AsyncSession, request_id: str, task_id: str) -> TaskORM:
    _task: TaskORM
    try:
        _task: TaskORM = await TaskORM.async_get(
            async_session=db_session, id=task_id, allow_no_result=False
        )
    except NoResultFound:
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.NOT_FOUND,
            detail=f"Not found task with '{task_id}' ID!",
        )
    except Exception:
        logger.exception(
            f"[{request_id}] - Failed to get task with '{task_id}' ID from database!"
        )
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.DATABASE_ERROR,
            detail=f"Failed to get task with '{task_id}' ID!",
        )

    return _task


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def async_update(
    db_session: AsyncSession, request_id: str, task_id: str, task_up: TaskBasePM
) -> TaskORM:
    _task: TaskORM
    try:
        _task: TaskORM = await TaskORM.async_update_by_id(
            async_session=db_session, id=task_id, **task_up.dict()
        )
    except NoResultFound:
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.NOT_FOUND,
            detail=f"Not found task with '{task_id}' ID!",
        )
    except Exception:
        logger.exception(
            f"[{request_id}] - Failed to update task with '{task_id}' ID into database!"
        )
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.DATABASE_ERROR,
            detail=f"Failed to update task with '{task_id}' ID!",
        )

    return _task


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def async_delete(db_session: AsyncSession, request_id: str, task_id: str):
    try:
        await TaskORM.async_delete_by_id(async_session=db_session, id=task_id)
    except NoResultFound:
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.NOT_FOUND,
            detail=f"Not found task with '{task_id}' ID!",
        )
    except Exception:
        logger.exception(
            f"[{request_id}] - Failed to delete task with '{task_id}' ID from database!"
        )
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.DATABASE_ERROR,
            detail=f"Failed to delete task with '{task_id}' ID!",
        )

    return


__all__ = [
    "async_get_list",
    "async_create",
    "async_get",
    "async_update",
    "async_delete",
]
