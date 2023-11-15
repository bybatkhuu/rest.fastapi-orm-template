# -*- coding: utf-8 -*-

from typing import Any, Union, Optional

from pydantic import Field, constr

from src.config import config
from src.core.constants.base import MethodEnum
from .base import ExtraBasePM, BasePM
from __version__ import __version__


class LinksResPM(ExtraBasePM):
    self_link: Optional[constr(strip_whitespace=True, max_length=2048)] = Field(
        default=None,
        alias="self",
        title="Self link",
        description="Link to the current resource.",
        examples=["/api/v1/resources"],
    )


class MetaResPM(ExtraBasePM):
    request_id: Optional[
        constr(strip_whitespace=True, min_length=32, max_length=36)
    ] = Field(
        default=None,
        title="Request ID",
        description="Current request ID.",
        examples=["211203afa2844d55b1c9d38b9f8a7063"],
    )
    method: Optional[MethodEnum] = Field(
        default=None,
        title="Method",
        description="Current request method.",
        examples=["GET"],
    )
    api_version: constr(strip_whitespace=True) = Field(
        default=config.api.version,
        min_length=1,
        max_length=16,
        title="API version",
        description="Current API version.",
        examples=[config.api.version],
    )
    version: constr(strip_whitespace=True) = Field(
        default=__version__,
        min_length=5,
        max_length=32,
        title="Version",
        description="Current service version.",
        examples=[__version__],
    )


class ErrorResPM(BasePM):
    code: constr(strip_whitespace=True) = Field(
        ...,
        min_length=3,
        max_length=36,
        title="Error code",
        description="Code that represents the error.",
        examples=["400_00000"],
    )
    description: Optional[constr(strip_whitespace=True)] = Field(
        default=None,
        max_length=512,
        title="Error description",
        description="Description of the error.",
        examples=["Bad request syntax or unsupported method."],
    )
    detail: Union[Any, dict, list] = Field(
        default=None,
        title="Error detail",
        description="Detail of the error.",
        examples=[
            {
                "loc": ["body", "field"],
                "msg": "Error message.",
                "type": "Error type.",
                "ctx": {"constraint": "value"},
            }
        ],
    )


class BaseResPM(BasePM):
    message: str = Field(
        ...,
        min_length=1,
        max_length=256,
        title="Message",
        description="Response message about the current request.",
        examples=["Successfully processed the request."],
    )
    data: Union[Any, dict, list] = Field(
        default=None,
        title="Data",
        description="Resource data or any data related to response.",
        examples=["Any data: dict, list, str, int, float, null, etc."],
    )
    links: LinksResPM = Field(
        default_factory=LinksResPM,
        title="Links",
        description="Links related to the current request or resource.",
    )
    meta: MetaResPM = Field(
        default_factory=MetaResPM,
        title="Meta",
        description="Meta information about the current request.",
    )
    error: Union[ErrorResPM, Any] = Field(
        default=None,
        title="Error",
        description="Error information about the current request.",
        examples=[None],
    )


## Error response schemas
class BadBaseResPM(BaseResPM):
    message: str = Field(
        ...,
        min_length=1,
        max_length=256,
        title="Message",
        description="Response message about the current request.",
        examples=["Bad Request!"],
    )
    data: Union[Any, dict, list] = Field(
        default=None,
        title="Data",
        description="Resource data or any response related data.",
        examples=[None],
    )
    error: Union[ErrorResPM, Any] = Field(
        default=None,
        title="Error",
        description="Error information about the current request.",
        examples=[
            {
                "code": "400_00000",
                "description": "Bad request syntax or unsupported method.",
                "detail": None,
            }
        ],
    )


class NotFoundBaseResPM(BadBaseResPM):
    message: str = Field(
        ...,
        min_length=1,
        max_length=256,
        title="Message",
        description="Response message about the current request.",
        examples=["Not Found!"],
    )
    error: Union[ErrorResPM, Any] = Field(
        default=None,
        title="Error",
        description="Error information about the current request.",
        examples=[
            {
                "code": "404_00000",
                "description": "Nothing matches the given URI.",
                "detail": "Not found any resource!",
            }
        ],
    )


class MethodNotBaseResPM(BadBaseResPM):
    message: str = Field(
        ...,
        min_length=1,
        max_length=256,
        title="Message",
        description="Response message about the current request.",
        examples=["Method Not Allowed!"],
    )
    error: Union[ErrorResPM, Any] = Field(
        default=None,
        title="Error",
        description="Error information about the current request.",
        examples=[
            {
                "code": "405_00000",
                "description": "Specified method is invalid for this resource.",
                "detail": None,
            }
        ],
    )


class InvalidBaseResPM(BadBaseResPM):
    message: str = Field(
        ...,
        min_length=1,
        max_length=256,
        title="Message",
        description="Response message about the current request.",
        examples=["Validation error!"],
    )
    error: Union[ErrorResPM, Any] = Field(
        default=None,
        title="Error",
        description="Error information about the current request.",
        examples=[
            {
                "code": "422_00000",
                "description": "Error description.",
                "detail": [
                    {
                        "loc": ["body", "field"],
                        "msg": "Error message.",
                        "type": "Error type.",
                        "ctx": {"constraint": "value"},
                    }
                ],
            }
        ],
    )


class ErrorBaseResPM(BadBaseResPM):
    message: str = Field(
        ...,
        min_length=1,
        max_length=256,
        title="Message",
        description="Response message about the current request.",
        examples=["Internal Server Error!"],
    )
    error: Union[ErrorResPM, Any] = Field(
        default=None,
        title="Error",
        description="Error information about the current request.",
        examples=[
            {
                "code": "500_00000",
                "description": "Server got itself in trouble.",
                "detail": None,
            }
        ],
    )


__all__ = [
    "LinksResPM",
    "MetaResPM",
    "ErrorResPM",
    "BaseResPM",
    "BadBaseResPM",
    "NotFoundBaseResPM",
    "MethodNotBaseResPM",
    "InvalidBaseResPM",
    "ErrorBaseResPM",
]
