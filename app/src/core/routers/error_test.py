# -*- coding: utf-8 -*-


from pydantic import Field

from fastapi import APIRouter, Request, Body, HTTPException

from src.core.constants import ErrorCodeEnum
from src.core.schemas import (
    BasePM,
    BaseResPM,
    BadBaseResPM,
    MethodNotBaseResPM,
    InvalidBaseResPM,
    ErrorBaseResPM,
)
from src.core.responses import BaseResponse
from src.core.exceptions import BaseHTTPException


router = APIRouter(tags=["Error Test"])


@router.get("/test", summary="Test", response_model=BaseResPM)
def get_test(request: Request):
    return BaseResponse(request=request, message="Test!")


@router.get("/error", summary="Error", status_code=500, response_model=ErrorBaseResPM)
def get_error():
    raise ValueError("Test ValueError!")


@router.get(
    "/exception", summary="Exception", status_code=400, response_model=BadBaseResPM
)
def get_http_exception():
    raise HTTPException(status_code=400, detail="Test HTTPException!")


@router.get(
    "/exception-detail",
    summary="Exception with detail",
    status_code=422,
    response_model=InvalidBaseResPM,
)
def get_http_exception_detail():
    raise HTTPException(
        status_code=422,
        detail={
            "message": "Test HTTPException with detail!",
            "error": ErrorCodeEnum.UNPROCESSABLE_ENTITY.value.dict(),
        },
    )


@router.get(
    "/exception-custom",
    summary="Custom exception",
    status_code=400,
    response_model=BadBaseResPM,
)
def get_base_http_exception():
    raise BaseHTTPException(
        error_enum=ErrorCodeEnum.BAD_REQUEST,
        message="Test BaseHTTPException!",
        description="Description test.",
        detail={"msg": "Detail test."},
    )


class Item(BasePM):
    name: str
    price: int = Field(..., ge=100)


@router.post(
    "/items/{item_id}",
    summary="Update item",
    responses={
        200: {"model": BaseResPM},
        405: {"model": MethodNotBaseResPM},
        422: {"model": InvalidBaseResPM},
    },
)
async def update_item(request: Request, item_id: int, item: Item = Body(...)):
    results = {"item_id": item_id, "item": item}
    return BaseResponse(request=request, message="Item updated!", content=results)


__all__ = ["router"]
