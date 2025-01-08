# -*- coding: utf-8 -*-

from typing import List, Tuple

from fastapi import APIRouter, Request, Depends, Path, Body, Query, HTTPException
from pydantic import constr
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import ALPHANUM_HYPHEN_REGEX
from api.core import utils
from api.config import config
from api.core.dependencies import db as db_deps
from api.core.responses import BaseResponse
from api.logger import logger

from .schemas import TaskBasePM, TaskUpPM, ResTaskPM, ResTasksPM
from .model import TaskORM
from . import service


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "/",
    summary="Get Task List",
    response_model=ResTasksPM,
    responses={422: {}},
)
async def get_tasks(
    request: Request,
    skip: int = Query(
        default=0,
        ge=0,
        title="Skip",
        description="Number of data to skip.",
        examples=[0],
    ),
    limit: int = Query(
        default=config.db.select_limit,
        ge=1,
        le=config.db.select_max_limit,
        title="Limit",
        description="Limit of data list.",
        examples=[100],
    ),
    is_desc: bool = Query(
        default=config.db.select_is_desc,
        title="Sort Direction",
        description="Is sort descending or ascending.",
        examples=[True],
    ),
    db_session: AsyncSession = Depends(db_deps.async_get_read),
):
    _request_id = request.state.request_id
    logger.info(f"[{_request_id}] - Getting task list...")

    _message = "Not found any task!"
    _orm_tasks: List[TaskORM] = []
    _links = {
        "first": None,
        "prev": None,
        "next": None,
        "last": None,
    }
    _list_count = 0
    _all_count = 0
    try:
        _result_tuple: Tuple[List[TaskORM], int] = await service.async_get_list(
            async_session=db_session,
            request_id=_request_id,
            offset=skip,
            limit=(limit + 1),
            is_desc=is_desc,
        )
        _orm_tasks, _all_count = _result_tuple

        _url = request.url.remove_query_params(["skip", "limit"])

        if 0 < _all_count:
            _links["first"] = utils.get_relative_url(
                _url.include_query_params(skip=0, limit=limit)
            )

            _last_skip = max((_all_count - 1) // limit * limit, 0)
            _links["last"] = utils.get_relative_url(
                _url.include_query_params(skip=_last_skip, limit=limit)
            )

        if 0 < skip:
            _prev_skip = max(skip - limit, 0)
            _links["prev"] = utils.get_relative_url(
                _url.include_query_params(skip=_prev_skip, limit=limit)
            )

        if limit < len(_orm_tasks):
            _orm_tasks = _orm_tasks[:limit]
            _links["next"] = utils.get_relative_url(
                _url.include_query_params(skip=(skip + limit), limit=limit)
            )

        _list_count = len(_orm_tasks)
        if 0 < _list_count:
            _message = "Successfully retrieved task list."

        logger.success(
            f"[{_request_id}] - Successfully retrieved task list count: {len(_orm_tasks)}/{_all_count}."
        )
    except Exception as err:
        if isinstance(err, HTTPException):
            raise

        logger.error(f"[{_request_id}] - Failed to get task list!")
        raise

    _response = BaseResponse(
        request=request,
        message=_message,
        content=_orm_tasks,
        links=_links,
        meta={
            "list_count": _list_count,
            "all_count": _all_count,
        },
        response_schema=ResTasksPM,
    )
    return _response


@router.post(
    "/",
    summary="Create Task",
    status_code=201,
    response_model=ResTaskPM,
    responses={422: {}},
)
async def create_task(
    request: Request,
    task_in: TaskBasePM = Body(
        ...,
        title="Task data",
        description="Task data to create.",
    ),
    db_session: AsyncSession = Depends(db_deps.async_get_write),
):
    _request_id = request.state.request_id
    logger.info(f"[{_request_id}] - Creating task with '{task_in.name}' name...")

    _task_orm: TaskORM
    try:
        _task_orm: TaskORM = await service.async_create(
            async_session=db_session, request_id=_request_id, task_in=task_in
        )
        await db_session.commit()

        logger.success(
            f"[{_request_id}] - Successfully created task with '{_task_orm.id}' ID."
        )
    except Exception as err:
        await db_session.rollback()

        if isinstance(err, HTTPException):
            raise

        logger.error(
            f"[{_request_id}] - Failed to create task with '{task_in.name}' name!"
        )
        raise

    _response = BaseResponse(
        request=request,
        status_code=201,
        message="Successfully created task.",
        content=_task_orm,
        response_schema=ResTaskPM,
    )
    return _response


@router.get(
    "/{task_id}",
    summary="Get Task",
    response_model=ResTaskPM,
    responses={404: {}, 422: {}},
)
async def get_task(
    request: Request,
    task_id: constr(strip_whitespace=True) = Path(  # type: ignore
        ...,
        min_length=8,
        max_length=64,
        regex=ALPHANUM_HYPHEN_REGEX,
        title="Task ID",
        description="Task ID to get.",
        examples=["tas1701388800_a0dc99d68d5e427eafe00525fac47012"],
    ),
    db_session: AsyncSession = Depends(db_deps.async_get_read),
):
    _request_id = request.state.request_id
    logger.info(f"[{_request_id}] - Getting task with '{task_id}' ID...")

    try:
        _task_orm: TaskORM = await service.async_get(
            async_session=db_session, request_id=_request_id, id=task_id
        )

        logger.success(
            f"[{_request_id}] - Successfully retrieved task with '{task_id}' ID."
        )
    except Exception as err:
        if isinstance(err, HTTPException):
            raise

        logger.error(f"[{_request_id}] - Failed to get task with '{task_id}' ID!")
        raise

    _response = BaseResponse(
        request=request,
        message="Successfully retrieved task info.",
        content=_task_orm,
        response_schema=ResTaskPM,
    )
    return _response


@router.put(
    "/{task_id}",
    summary="Update Task",
    response_model=ResTaskPM,
    responses={404: {}, 422: {}},
)
async def update_task(
    request: Request,
    task_id: constr(strip_whitespace=True) = Path(  # type: ignore
        ...,
        min_length=8,
        max_length=64,
        regex=ALPHANUM_HYPHEN_REGEX,
        title="Task ID",
        description="Task ID to update.",
        examples=["tas1701388800_cd388fca74de4e8085df41e7c6df762e"],
    ),
    task_up: TaskUpPM = Body(
        ..., title="Task data", description="Task data to update."
    ),
    db_session: AsyncSession = Depends(db_deps.async_get_write),
):
    _request_id = request.state.request_id
    logger.info(f"[{_request_id}] - Updating task with '{task_id}' ID...")

    _task_orm: TaskORM
    try:
        _task_orm: TaskORM = await service.async_update(
            async_session=db_session,
            request_id=_request_id,
            id=task_id,
            **task_up.model_dump(exclude_unset=True),
        )
        await db_session.commit()

        logger.success(
            f"[{_request_id}] - Successfully updated task with '{task_id}' ID."
        )
    except Exception as err:
        await db_session.rollback()

        if isinstance(err, HTTPException):
            raise

        logger.error(f"[{_request_id}] - Failed to update task with '{task_id}' ID!")
        raise

    _response = BaseResponse(
        request=request,
        message="Successfully updated task.",
        content=_task_orm,
        response_schema=ResTaskPM,
    )
    return _response


@router.delete(
    "/{task_id}",
    summary="Delete Task",
    status_code=204,
    responses={404: {}, 422: {}},
)
async def delete_task(
    request: Request,
    task_id: str = Path(
        ...,
        min_length=8,
        max_length=64,
        regex=ALPHANUM_HYPHEN_REGEX,
        title="Task ID",
        description="Task ID to delete.",
        examples=["tas1701388800_cd388fca74de4e8085df41e7c6df762e"],
    ),
    db_session: AsyncSession = Depends(db_deps.async_get_write),
):
    _request_id = request.state.request_id
    logger.info(f"[{_request_id}] - Deleting task with '{task_id}' ID...")

    try:
        await service.async_delete(
            async_session=db_session, request_id=_request_id, id=task_id
        )
        await db_session.commit()

        logger.success(
            f"[{_request_id}] - Successfully deleted task with '{task_id}' ID."
        )
    except Exception as err:
        await db_session.rollback()

        if isinstance(err, HTTPException):
            raise

        logger.error(f"[{_request_id}] - Failed to delete task with '{task_id}' ID!")
        raise

    return


__all__ = ["router"]
