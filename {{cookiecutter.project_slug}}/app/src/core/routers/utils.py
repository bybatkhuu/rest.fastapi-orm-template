# -*- coding: utf-8 -*-

from fastapi import APIRouter, Request

from src.config import config
from src.core.schemas import BaseResPM
from src.core.responses import BaseResponse
from src.databases.rdb import (
    async_write_engine,
    async_read_engine,
    async_is_db_connectable,
)

router = APIRouter(tags=config.api.routes.utils["_tags"])


@router.get(
    "/",
    summary="Base",
    description="Base path for all REST API endpoints.",
    response_model=BaseResPM,
)
async def get_base(request: Request):
    return BaseResponse(
        request=request, message="Welcome to the FastAPI ORM Template service."
    )


@router.get(
    config.api.routes.utils["ping"],
    summary="Ping",
    description="Check if the service is up and running.",
    response_model=BaseResPM,
)
async def get_ping(request: Request):
    return BaseResponse(
        request=request, message="Pong!", headers={"Cache-Control": "no-cache"}
    )


@router.get(
    config.api.routes.utils["health"],
    summary="Health",
    description="Check health of all related backend services.",
    response_model=BaseResPM,
)
async def get_health(request: Request):
    _message = "Some services are not available or not working properly!"

    _data = {
        "DB": {
            "write": {
                "message": "Can't connect to the write database!",
                "is_alive": False,
            },
            "read": {
                "message": "Can't connect to the read database!",
                "is_alive": False,
            },
        }
    }

    _is_write_db = False
    if await async_is_db_connectable(async_engine=async_write_engine):
        _data["DB"]["write"] = {
            "message": "Write database is up and connected.",
            "is_alive": True,
        }
        _is_write_db = True

    _is_read_db = False
    if await async_is_db_connectable(async_engine=async_read_engine):
        _data["DB"]["read"] = {
            "message": "Read database is up and connected.",
            "is_alive": True,
        }
        _is_read_db = True

    if _is_write_db and _is_read_db:
        _message = "Everything is OK."

    return BaseResponse(
        request=request,
        content=_data,
        message=_message,
        headers={"Cache-Control": "no-cache"},
    )


__all__ = ["router"]
