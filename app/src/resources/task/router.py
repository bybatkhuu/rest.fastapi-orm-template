# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple

from fastapi import APIRouter, Request, Depends, Path, Body, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import ErrorCodeEnum
from src.config import config
from src.core.dependencies.db import async_get_read_db, async_get_write_db
from src.core.schemas import InvalidBaseResPM, NotFoundBaseResPM
from src.core.responses import BaseResponse
from src.core.exceptions import BaseHTTPException
from src.resources.task.schemas import TaskBasePM, ResTaskPM, ResTasksPM
from src.resources.task.models import TaskORM
from src.resources.task import service
from src.logger import logger


router = APIRouter(
    prefix=config.api.routes.tasks["_prefix"],
    tags=config.api.routes.tasks["_tags"],
)


@router.get(
    "/",
    summary="Get Task List",
    response_model=ResTasksPM,
    responses={422: {"model": InvalidBaseResPM}},
)
async def get_tasks(
    request: Request,
    name: Optional[str] = Query(
        default=None,
        min_length=2,
        max_length=64,
        title="Task name",
        description="Name of the task.",
        examples=["Task 1"],
    ),
    point: Optional[int] = Query(
        default=None,
        ge=0,
        le=100,
        title="Task point",
        description="Point of the task.",
        examples=[70],
    ),
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
        le=config.db.max_select_limit,
        title="Limit",
        description="Limit of data list.",
        examples=[100],
    ),
    db_session: AsyncSession = Depends(async_get_read_db),
):
    """
    ### Features

    * Get task list with pagination (`skip`, `limit`).
    * Filter task list by `name` and `point`.
    """

    _response: BaseResponse
    _request_id = request.state.request_id

    _kwargs = {}
    if name:
        _kwargs["name"] = name

    if point:
        _kwargs["point"] = point

    try:
        _result: Tuple[List[TaskORM], int] = await service.async_get_list(
            db_session=db_session,
            request_id=_request_id,
            skip=skip,
            limit=(limit + 1),
            **_kwargs,
        )
        _tasks, _total_count = _result

        _url_path = request.url.path + "?"
        if request.url.query:
            _url_path += request.url.remove_query_params(["skip", "limit"]).query + "&"

        _links = {
            "first": None,
            "prev": None,
            "next": None,
            "last": None,
        }

        if 0 < _total_count:
            _links["first"] = f"{_url_path}skip=0&limit={limit}"

            _last_skip = int(_total_count / limit) * limit
            if _last_skip == _total_count:
                _last_skip = _last_skip - limit
            _links["last"] = f"{_url_path}skip={_last_skip}&limit={limit}"

        _list_count = len(_tasks)
        if _list_count == (limit + 1):
            _tasks = _tasks[:limit]
            _list_count = len(_tasks)
            _links["next"] = f"{_url_path}skip={skip + limit}&limit={limit}"

        if 0 < skip:
            _prev_skip = skip - limit
            if _prev_skip < 0:
                _prev_skip = 0
            _links["prev"] = f"{_url_path}skip={_prev_skip}&limit={limit}"

        _message = "Not found any task!"
        if 0 < _list_count:
            _message = "Suceessfully retrieved task list."

        _response = BaseResponse(
            message=_message,
            content=_tasks,
            links=_links,
            meta={
                "list_count": _list_count,
                "total_count": _total_count,
            },
            request=request,
            response_schema=ResTasksPM,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"[{_request_id}] - Failed to get task list!")
        raise BaseHTTPException(
            error_enum=ErrorCodeEnum.INTERNAL_SERVER_ERROR,
            message="Failed to get task list!",
        )
    return _response


@router.post(
    "/",
    summary="Create Task",
    status_code=201,
    response_model=ResTaskPM,
    responses={422: {"model": InvalidBaseResPM}},
)
async def create_task(
    request: Request,
    task_in: TaskBasePM = Body(
        ...,
        title="Task data",
        description="Task data to create.",
        examples=[{"name": "Task 1", "point": 70}],
    ),
    db_session: AsyncSession = Depends(async_get_write_db),
):
    _response: BaseResponse
    _request_id = request.state.request_id
    try:
        _task: TaskORM = await service.async_create(
            db_session=db_session, request_id=_request_id, task_in=task_in
        )

        _response = BaseResponse(
            message="Successfully created task.",
            content=_task,
            request=request,
            response_schema=ResTaskPM,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"[{_request_id}] - Failed to create task!")

    return _response


@router.get(
    config.api.routes.tasks["task"],
    summary="Get Task",
    response_model=ResTaskPM,
    responses={
        404: {"model": NotFoundBaseResPM},
        422: {"model": InvalidBaseResPM},
    },
)
async def get_task(
    request: Request,
    task_id: str = Path(
        ...,
        title="Task ID",
        description="Task ID to get.",
        examples=["TAS1699928748406212_46D46E7E55FA4A6E8478BD6B04195793"],
    ),
    db_session: AsyncSession = Depends(async_get_read_db),
):
    _response: BaseResponse
    _request_id = request.state.request_id
    try:
        _task: TaskORM = await service.async_get(
            db_session=db_session, request_id=_request_id, task_id=task_id
        )

        _response = BaseResponse(
            message="Successfully retrieved task info.",
            content=_task,
            request=request,
            response_schema=ResTaskPM,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"[{_request_id}] - Failed to get task with '{task_id}' ID!")

    return _response


@router.put(
    config.api.routes.tasks["task"],
    summary="Update Task",
    response_model=ResTaskPM,
    responses={
        404: {"model": NotFoundBaseResPM},
        422: {"model": InvalidBaseResPM},
    },
)
async def update_task(
    request: Request,
    task_id: str = Path(
        ...,
        title="Task ID",
        description="Task ID to update.",
        examples=["TAS1699928748406212_46D46E7E55FA4A6E8478BD6B04195793"],
    ),
    task_up: TaskBasePM = Body(
        ...,
        title="Task data",
        description="Task data to update.",
        examples=[{"name": "Task 1", "point": 70}],
    ),
    db_session: AsyncSession = Depends(async_get_write_db),
):
    _response: BaseResponse
    _request_id = request.state.request_id
    try:
        _task: TaskORM = await service.async_update(
            db_session=db_session,
            request_id=_request_id,
            task_id=task_id,
            task_up=task_up,
        )

        _response = BaseResponse(
            message="Successfully updated task.",
            content=_task,
            request=request,
            response_schema=ResTaskPM,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception(
            f"[{_request_id}] - Failed to update task with '{task_id}' ID!"
        )

    return _response


@router.delete(
    config.api.routes.tasks["task"],
    summary="Delete Task",
    status_code=204,
    responses={
        404: {"model": NotFoundBaseResPM},
        422: {"model": InvalidBaseResPM},
    },
)
async def delete_task(
    request: Request,
    task_id: str = Path(
        ...,
        title="Task ID",
        description="Task ID to delete.",
        examples=["TAS1699928748406212_46D46E7E55FA4A6E8478BD6B04195793"],
    ),
    db_session: AsyncSession = Depends(async_get_write_db),
):
    _request_id = request.state.request_id
    try:
        await service.async_delete(
            db_session=db_session, request_id=_request_id, task_id=task_id
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception(
            f"[{_request_id}] - Failed to delete task with '{task_id}' ID!"
        )

    return


__all__ = ["router"]
