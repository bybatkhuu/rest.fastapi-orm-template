# -*- coding: utf-8 -*-

from datetime import datetime
from typing import List, Optional

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import validate_arguments

from src.config import config
from src.core.constants.error_code import ErrorCodeEnum
from src.core.exceptions import BaseHTTPException
from src.resources.task.schemas import TaskBasePM
from src.resources.task.models import TaskORM
from src.logger import logger


@validate_arguments(config=dict(arbitrary_types_allowed=True))
def get_test(
    db_session: Session,
) -> dict:
    # _result = TaskORM.get_by_where(
    #     session=db_session,
    #     where={"column": "id", "value": "ffb4245f0331377d2c475c4a396b8e0b"},
    # )

    _result = TaskORM.select_by_where(session=db_session, where=[])

    # print("Result: ", _result)
    return {"message": "Hello World!"}


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def async_get_test(
    db_session: AsyncSession,
) -> dict:
    _tasks: List[TaskORM] = await TaskORM.async_select_by_where(
        async_session=db_session, where={"column": "name", "value": "Auditor"}
    )

    _tasks: List[TaskORM] = await TaskORM.async_update_objects(
        async_session=db_session, orm_objects=_tasks, updated_at=datetime.utcnow()
    )

    for _task in _tasks:
        print(f"Result: {_task}")

    print()

    return {"message": "Hello World!"}


@validate_arguments(config=dict(arbitrary_types_allowed=True))
async def async_get_list(
    db_session: AsyncSession,
    request_id: str,
    name: Optional[str] = None,
    skip: int = 0,
    limit: int = config.db.select_limit,
) -> List[TaskORM]:
    _tasks: List[TaskORM] = []
    try:
        _where = []
        if name:
            _where.append({"op": "like", "column": "name", "value": name})

        _tasks: List[TaskORM] = await TaskORM.async_select_by_where(
            async_session=db_session, where=_where, offset=skip, limit=limit
        )

    except Exception:
        logger.exception(f"[{request_id}] - Failed to get task list from database!")
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.DATABASE_ERROR,
            message="Failed to get task list!",
        )

    return _tasks


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
