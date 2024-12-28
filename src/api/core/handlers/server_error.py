# -*- coding: utf-8 -*-

from fastapi import Request

from beans_logging_fastapi import async_log_http_error

from src.core.constants import ErrorCodeEnum
from src.config import config
from src.core.responses import BaseResponse


## For unhandled Exception or 500 internal server error:
async def server_error_handler(request: Request, exc: Exception) -> BaseResponse:
    """Error handler for any kind of unhandled Exception or 500 internal server error.

    Args:
        request (Request  , required): Request object from FastAPI.
        exc     (Exception, required): Any kind of Exception object.

    Returns:
        BaseResponse: Response object.
    """

    _status_code = 500
    _error = ErrorCodeEnum.INTERNAL_SERVER_ERROR.value.dict()
    if config.debug:
        _error["detail"] = str(exc)

    _message: str = _error.get("message")

    await async_log_http_error(
        request=request,
        status_code=_status_code,
        msg_format=config.logger.extra.http_std_error_format,
    )
    return BaseResponse(
        request=request, status_code=_status_code, message=_message, error=_error
    )


__all__ = ["server_error_handler"]
